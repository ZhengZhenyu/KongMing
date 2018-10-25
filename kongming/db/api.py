# Copyright 2017 Huawei Technologies Co.,LTD.
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

"""Base classes for storage engines."""

import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six


_BACKEND_MAPPING = {'sqlalchemy': 'kongming.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF,
                                backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    # InstanceCPUMapping
    @abc.abstractmethod
    def instance_cpu_mapping_list(
            self, context, limit, marker, sort_key, sort_dir, project_only):
        """Return a list of Mapping objects."""

    @abc.abstractmethod
    def instance_cpu_mapping_get(cls, context, instance_uuid):
        """Find a Mapping and return a Mapping object."""
        return mapping

    @abc.abstractmethod
    def instance_cpu_mapping_create(self, context=None):
        """Create a Mapping record in the DB."""

    @abc.abstractmethod
    def instance_cpu_mapping_destroy(self, context=None):
        """Delete the Mapping from the DB."""

    @abc.abstractmethod
    def instance_cpu_mapping_update(self, context, instance_uuid, values):
        """Update a Mapping"""

    @abc.abstractmethod
    def host_get_by_name(self, context, host_name):
        """Get host by name."""

    @abc.abstractmethod
    def host_update(self, context, host_name, updates):
        """Update host by name."""

    @abc.abstractmethod
    def host_create(self, context, values):
        """Create a new host."""

    @abc.abstractmethod
    def instance_update(self, context, uuid, updates):
        """Update instance by uuid."""

    @abc.abstractmethod
    def instance_create(self, context, values):
        """Create a new instance."""

    @abc.abstractmethod
    def instance_get(self, context, uuid):
        """Get an instance by uuid"""

    @abc.abstractmethod
    def instances_get_by_host_name(self, context, host_name):
        """Get a list of instances by hostname"""
