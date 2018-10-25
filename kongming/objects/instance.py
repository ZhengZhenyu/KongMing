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
class Instance(base.KongmingObject,
               object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=True),
        'status': object_fields.StringField(nullable=True),
        'host': object_fields.StringField(nullable=True),
        'cpu_mappings': object_fields.FlexibleDictField(
            nullable=True),
    }

    def __init__(self, context=None, **kwargs):
        super(Instance, self).__init__(context=context, **kwargs)

    @staticmethod
    def _from_db_object(context, instance, db_instance, expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = []

        for name, field in instance.fields.items():
            value = db_instance[name]
            if isinstance(field, object_fields.IntegerField):
                value = value if value is not None else 0
            instance[name] = value

        instance.obj_reset_changes()
        return instance

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects"""

        return [Instance._from_db_object(context, cls(context), obj)
                for obj in db_objects]

    @classmethod
    def list(cls, context):
        """Return a list of Mapping objects."""
        db_instances = cls.dbapi.instance_list(context)
        return Instance._from_db_object_list(
            db_instances, cls, context)

    @classmethod
    def get(cls, context, instance_uuid):
        """Find a Mapping and return a Mapping object."""
        db_instance = cls.dbapi.instance_get(context, instance_uuid)
        instance = Instance._from_db_object(
            context, cls(context), db_instance)
        return instance

    def create(self, context=None):
        """Create a Mapping record in the DB."""
        values = self.obj_get_changes()
        db_instance = self.dbapi.instance_create(context, values)
        self._from_db_object(context, self, db_instance)

    def destroy(self, context=None):
        """Delete the Mapping from the DB."""
        self.dbapi.instance_destroy(context, self.uuid)
        self.obj_reset_changes()

    def save(self, context=None):
        updates = self.obj_get_changes()

        if updates:
            self.dbapi.instance_update(
                context, self.uuid, updates)


@base.KongmingObjectRegistry.register
class InstanceList(base.ObjectListBase,
                   base.KongmingObject,
                   object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial Version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'objects': object_fields.ListOfObjectsField('Instance'),
    }