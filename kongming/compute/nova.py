from distutils.version import LooseVersion
import functools
import os
import six
import sys

from oslo_config import cfg
from oslo_utils import encodeutils

from keystoneauth1 import loading as ka_loading
from keystoneclient import exceptions as keystone_exceptions

from novaclient import client as nova_client
from novaclient import exceptions as nova_exceptions

from kongming.common import exception


client_opts = [
    cfg.StrOpt('os-region-name',
               default=os.environ.get('OS_REGION_NAME'),
               help='Region name to use for OpenStack service endpoints.'
                    'If set, will be included in plugin mappings.'),
    cfg.StrOpt('os-endpoint-type',
               default=os.environ.get('OS_ENDPOINT_TYPE', 'publicURL'),
               help='Type of endpoint in Identity service catalog to '
                    'use for communication with OpenStack services.'),
]

GROUP = "service_credentials"
CONF = cfg.CONF

CONF.register_opts(client_opts, group=GROUP)

ka_loading.register_session_conf_options(CONF, GROUP)
ka_loading.register_auth_conf_options(CONF, GROUP)

_session = None

NOVA_MIN_API_VERSION = '2.1'


def _get_session():
    global _session
    if not _session:
        auth = ka_loading.load_auth_from_conf_options(CONF, GROUP)
        _session = ka_loading.load_session_from_conf_options(
            CONF, GROUP, auth=auth)
    return _session


def get_novaclient():

    def do_get_client(api_version=2.1):
        session = _get_session()
        return nova_client.Client(
            version=api_version,
            session=session,
            region_name=CONF.service_credentials.os_region_name,
            endpoint_type=CONF.service_credentials.os_endpoint_type
        )

    version = CONF["service_credentials:nova"].compute_api_version
    # Check whether Nova can support the provided microversion.
    max_version = do_get_client().versions.list()[-1].version
    if LooseVersion(version) > LooseVersion(max_version) or \
            LooseVersion(version) < LooseVersion(NOVA_MIN_API_VERSION):
        raise exception.InvalidAPIVersionProvided(
            service='compute service', min_version=NOVA_MIN_API_VERSION,
            max_version=max_version)

    return do_get_client(version)


def _reraise(desired_exc):
    six.reraise(type(desired_exc), desired_exc, sys.exc_info()[2])


def translate_nova_exception(method):
    """Transforms a cinder exception but keeps its traceback intact."""
    @functools.wraps(method)
    def wrapper(self, ctx, *args, **kwargs):
        try:
            res = method(self, ctx, *args, **kwargs)
        except (nova_exceptions.ConnectionError,
                keystone_exceptions.ConnectionError) as exc:
            err_msg = encodeutils.exception_to_unicode(exc)
            _reraise(exception.NovaConnectionFailed(reason=err_msg))
        except (keystone_exceptions.BadRequest,
                nova_exceptions.BadRequest)as exc:
            err_msg = encodeutils.exception_to_unicode(exc)
            _reraise(exception.BadRequest(reason=err_msg))
        except (keystone_exceptions.Forbidden,
                nova_exceptions.Forbidden):
            _reraise(exception.NotAuthorized())
        except (keystone_exceptions.NotFound,
                nova_exceptions.NotFound) as exc:
            err_msg = encodeutils.exception_to_unicode(exc)
            _reraise(exception.InstanceNotFound(reason=err_msg))
        return res
    return wrapper


class API(object):

    @translate_nova_exception
    def get_instance(self, context, instance_uuid):
        client = get_novaclient()
        client.servers.get(instance_uuid).to_dict()
