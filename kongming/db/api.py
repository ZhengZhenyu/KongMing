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

    # Mappings
    @abc.abstractmethod
    def list(cls, context):
        """Return a list of Mapping objects."""

    @abc.abstractmethod
    def get(cls, context, mapping_uuid):
        """Find a Mapping and return a Mapping object."""
        return mapping

    @abc.abstractmethod
    def create(self, context=None):
        """Create a Mapping record in the DB."""

    @abc.abstractmethod
    def destroy(self, context=None):
        """Delete the Mapping from the DB."""

    @abc.abstractmethod
    def save(self, context=None):
        """Update a Mapping"""
