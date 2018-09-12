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

from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from kongming.db import api as dbapi
from kongming.objects import base
from kongming.objects import fields as object_fields


LOG = logging.getLogger(__name__)


@base.KongmingObjectRegistry.register
class InstanceCPUMapping(base.KongmingObject,
                         object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': object_fields.IntegerField(nullable=False),
        'instance_uuid': object_fields.UUIDField(nullable=False),
        'project_id': object_fields.UUIDField(nullable=False),
        'user_id': object_fields.UUIDField(nullable=False),
        'cpu_mappings': object_fields.StringField(nullable=True),
        'host': object_fields.StringField(nullable=True),
        'status': object_fields.StringField(nullable=True)
    }

    def __init__(self, *args, **kwargs):
        super(InstanceCPUMapping, self).__init__(*args, **kwargs)
        self._orig_projects = {}

    @staticmethod
    def _from_db_object(context, mapping, db_mapping, expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = []

        for name, field in mapping.fields.items():
            value = db_mapping[name]
            if isinstance(field, object_fields.IntegerField):
                value = value if value is not None else 0
            mapping[name] = value

        mapping.obj_reset_changes()
        return mapping

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects"""

        return [InstanceCPUMapping._from_db_object(context, cls(context), obj)
                for obj in db_objects]

    @classmethod
    def list(cls, context):
        """Return a list of Mapping objects."""
        db_mappings = cls.dbapi.instance_cpu_mapping_list(context)
        return InstanceCPUMapping._from_db_object_list(
            db_mappings, cls, context)

    @classmethod
    def get(cls, context, mapping_uuid):
        """Find a Mapping and return a Mapping object."""
        db_mapping = cls.dbapi.instance_cpu_mapping_get(context, mapping_uuid)
        mapping = InstanceCPUMapping._from_db_object(
            context, cls(context), db_mapping)
        return mapping

    def create(self, context=None):
        """Create a Mapping record in the DB."""
        values = self.obj_get_changes()
        db_mapping = self.dbapi.instance_cpu_mapping_create(context, values)
        self._from_db_object(context, self, db_mapping)

    def destroy(self, context=None):
        """Delete the Mapping from the DB."""
        self.dbapi.instance_cpu_mapping_destroy(context, self.uuid)
        self.obj_reset_changes()

    def save(self, context=None):
        updates = self.obj_get_changes()

        if updates:
            self.dbapi.instance_cpu_mapping_update(
                context, self.uuid, updates)