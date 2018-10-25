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
from kongming import objects
from kongming.objects import base
from kongming.objects import fields as object_fields

LOG = logging.getLogger(__name__)


OPTIONAL_ATTRS = ['instances']


@base.KongmingObjectRegistry.register
class Host(base.KongmingObject, object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': object_fields.IntegerField(),
        'host_name': object_fields.StringField(nullable=True),
        'cpu_topology': object_fields.FlexibleDictField(
            nullable=True),
        'instances': object_fields.ListOfObjectsField(
            'Instance', nullable=True)
    }

    def __init__(self, context=None, **kwargs):
        super(Host, self).__init__(context=context, **kwargs)

    @staticmethod
    def _from_db_object(context, host, db_host, expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = []

        for name, field in host.fields.items():
            if name not in OPTIONAL_ATTRS:
                value = db_host[name]
                if isinstance(field, object_fields.IntegerField):
                    value = value if value is not None else 0
                host[name] = value

        if 'instances' in expected_attrs:
            host._load_instances(host._context, host.host_name)

        host.obj_reset_changes()
        return host

    @staticmethod
    def _from_db_object_list(db_objects, cls, context, expect_attrs=None):
        """Converts a list of database entities to a list of formal objects"""

        return [Host._from_db_object(
            context, cls(context), obj, expected_attrs=expect_attrs)
            for obj in db_objects]

    def _load_instances(self, context, host_name):
        self.instances = objects.Instance.get_instances_by_host_name(
            context=context, host_name=host_name).objects

    @classmethod
    def list(cls, context):
        """Return a list of Mapping objects."""
        db_hosts = cls.dbapi.host_list(context)
        return Host._from_db_object_list(
            db_hosts, cls, context)

    @classmethod
    def get(cls, context, host_name, expected_attrs=None):
        """Find a Mapping and return a Mapping object."""
        db_host = cls.dbapi.host_get_by_name(context, host_name)
        host = Host._from_db_object(
            context, cls(context), db_host, expected_attrs)
        return host

    def create(self, context=None):
        """Create a Mapping record in the DB."""
        values = self.obj_get_changes()
        db_host = self.dbapi.host_create(context, values)
        self._from_db_object(context, self, db_host)

    def destroy(self, context=None):
        """Delete the Mapping from the DB."""
        self.dbapi.host_destroy(context, self.host_name)
        self.obj_reset_changes()

    def save(self, context=None):
        updates = self.obj_get_changes()

        if updates:
            self.dbapi.host_update(
                context, self.host_name, updates)
