# Copyright 2018 Huawei Technologies Co.,LTD.
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

import pecan
from pecan import rest
from six.moves import http_client
import wsme
from wsme import types as wtypes

from oslo_log import log

from kongming.api.controllers import base
from kongming.api.controllers import link
from kongming.api.controllers.v1 import types
from kongming.api.controllers.v1 import utils as api_utils
from kongming.api import expose
from kongming.common import exception
from kongming.common import policy
from kongming.common import clients
from kongming.common import states
from kongming import compute
from kongming import objects


LOG = log.getLogger(__name__)


class Host(base.APIBase):
    """API representation of a Host.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of
    a host.
    """

    host_name = wtypes.text
    """The name of the host"""

    cpu_topology = types.jsontype
    """The cpu topology of the host"""

    instances = [types.jsontype]
    """The instances on this host"""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        self.fields = []
        for field in objects.Host.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_host):
        api_host = cls(**obj_host.as_dict())
        url = pecan.request.public_url
        api_host.links = [
            link.Link.make_link(
                'self', url, 'hosts',
                api_host.host_name),
            link.Link.make_link(
                'bookmark', url, 'hosts',
                api_host.host_name,
                bookmark=True)
            ]
        return api_host


class HostCollection(base.APIBase):
    """API representation of a collection of Host."""

    hosts = [Host]
    """A list containing host objects"""

    @classmethod
    def convert_with_links(cls, obj_hosts):
        collection = cls()
        collection.hosts = [
            Host.convert_with_links(obj_host)
            for obj_host in obj_hosts]
        return collection


class HostsController(rest.RestController):
    """REST controller for Host."""

    @policy.authorize_wsgi("kongming:host", "get")
    @expose.expose(Host, types.string)
    def get_one(self, host_name):
        """Retrieve information about the given host.

        :param host_name: name of the host.
        """
        db_host = objects.Host.get(
            pecan.request.context, host_name, expected_attrs=['instances'])
        return Host.convert_with_links(db_host)
