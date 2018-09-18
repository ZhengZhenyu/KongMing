# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from distutils.version import LooseVersion
import functools
import os
import six
import sys

from kongming.common.i18n import _ #noqa

from nova.scheduler import filters
from oslo_config import cfg
from oslo_log import log as logging

from keystoneauth1 import loading as ka_loading
from keystoneclient import exceptions as keystone_exceptions

from kongmingclient.v1 import client as kongming_client

LOG = logging.getLogger(__name__)

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

GROUP = "kongming_credentials"
CONF = cfg.CONF

CONF.register_opts(client_opts, group=GROUP)

ka_loading.register_session_conf_options(CONF, GROUP)
ka_loading.register_auth_conf_options(CONF, GROUP)

_km_session = None

def _get_session():
    global _km_session
    if not _km_session:
        auth = ka_loading.load_auth_from_conf_options(CONF, GROUP)
        _km_session = ka_loading.load_session_from_conf_options(
            CONF, GROUP, auth=auth)
    return _km_session


def get_kongmingclient():
    session = _get_session()

    return kongming_client.Client(
        session=session,
        region_name=CONF.kongming_credentials.os_region_name,
        endpoint_type=CONF.kongming_credentials.os_endpoint_type
    )


class KongmingFilter(filters.BaseHostFilter):
    """KongMing Filter for nova-scheduler."""

    run_filter_once_per_request = True

    def resource_pin_request(self, host_state, spec_obj, requested_mapping):

        # 1. store requested mapping in KongMing
        client = get_kongmingclient()
        try:
            client.instance_cpu_mappings.create(
            instance_uuid=spec_obj.instance_uuid,
            cpu_mappings=requested_mapping,
            wait_until_active=True)
        except Exception:
            LOG.debug("Unable to connect to kongming, PASS.")
            return True
        # 2. Perform filtering process
        # To Do

        return True

    def host_passes(self, host_state, spec_obj):
        """
        Check for hosts' CPU/NUMA ability and store mapping in Kongming.
        """

        # Find which Pools the user wants to use (if any)
        requested_mapping = spec_obj.get_scheduler_hint('resource_pin')

        # the request is host reservation
        if requested_mapping:
            return self.resource_pin_request(host_state, spec_obj,
                                             requested_mapping)

        return True
