# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.version import LooseVersion
import os

from novaclient import client as nova_client
from keystoneauth1 import loading as ka_loading
from keystoneclient import exceptions as keystone_exceptions
from kongming.common import exception

from oslo_config import cfg

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

compute_api_version = cfg.StrOpt(
    'compute_api_version',
    default='2.1',
    help='The compute API (micro)version, the provided '
         'compute API (micro)version should be not smaller '
         'than 2.1 and not larger than the max supported '
         'Compute API microversion. The current supported '
         'Compute API versions can be checked using: '
         'nova version-list.')

GROUP = "service_credentials"
CONF = cfg.CONF

CONF.register_opts(client_opts, group=GROUP)
CONF.register_opt(compute_api_version, group="service_credentials:nova")

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
