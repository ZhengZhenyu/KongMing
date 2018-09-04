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

"""SQLAlchemy storage backend."""

import threading
import copy

from oslo_db import api as oslo_db_api
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as sqlalchemyutils
from oslo_log import log
from oslo_utils import strutils
from oslo_utils import uuidutils
from sqlalchemy.orm.exc import NoResultFound

from kongming.common import exception
from kongming.common.i18n import _
from kongming.db import api
from kongming.db.sqlalchemy import models


_CONTEXT = threading.local()
LOG = log.getLogger(__name__)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def _session_for_read():
    return enginefacade.reader.using(_CONTEXT)


def _session_for_write():
    return enginefacade.writer.using(_CONTEXT)


def model_query(context, model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param context: Context of the query
    :param model: Model to query. Must be a subclass of ModelBase.
    :param args: Arguments to query. If None - model is used.

    Keyword arguments:

    :keyword project_only:
      If set to True, then will do query filter with context's project_id.
      if set to False or absent, then will not do query filter with context's
      project_id.
    :type project_only: bool
    """

    if kwargs.pop("project_only", False):
        kwargs["project_id"] = context.tenant

    with _session_for_read() as session:
        query = sqlalchemyutils.model_query(
            model, session, args, **kwargs)
        return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if strutils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def _paginate_query(context, model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(context, model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = sqlalchemyutils.paginate_query(query, model, limit, sort_keys,
                                               marker=marker,
                                               sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exception.InvalidParameterValue(
            _('The sort_key value "%(key)s" is an invalid field for sorting')
            % {'key': sort_key})
    return query.all()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    @oslo_db_api.retry_on_deadlock
    def instance_cpu_mapping_create(self, context, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        mapping = models.InstanceCPUMapping()
        mapping.update(values)

        with _session_for_write() as session:
            try:
                session.add(mapping)
                session.flush()
            except db_exc.DBDuplicateEntry:
                raise exception.InstanceCPUMappingAlreadyExists(
                    uuid=values['uuid'])
            return mapping

    def instance_cpu_mapping_get(self, context, mapping_uuid):
        query = model_query(
            context,
            models.InstanceCPUMapping).filter_by(uuid=mapping_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstanceCPUMappingNotFound(uuid=mapping_uuid)

    def instance_cpu_mapping_list(
            self, context, limit, marker, sort_key, sort_dir, project_only):
        query = model_query(context, models.InstanceCPUMapping,
                            project_only=project_only)
        return _paginate_query(context, models.InstanceCPUMapping, limit,
                               marker, sort_key, sort_dir, query)

    def instance_cpu_mapping_update(self, context, uuid, values):
        if 'instance_uuid' in values:
            msg = _("Cannot overwrite instance_uuid for an existing Mapping.")
            raise exception.InvalidParameterValue(err=msg)
        if 'uuid' in values:
            msg = _("Cannot overwrite uuid for an existing Mapping.")
            raise exception.InvalidParameterValue(err=msg)
        if 'id' in values:
            msg = _("Cannot overwrite id for an existing Mapping.")
            raise exception.InvalidParameterValue(err=msg)

        return self._do_update_instance_cpu_mapping(context, uuid, values)

    @oslo_db_api.retry_on_deadlock
    def _do_update_instance_cpu_mapping(self, context, uuid, values):
        with _session_for_write():
            query = model_query(context, models.InstanceCPUMapping)
            query = add_identity_filter(query, uuid)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.InstanceCPUMappingNotFound(uuid=uuid)

            ref.update(values)
        return ref

    @oslo_db_api.retry_on_deadlock
    def instance_cpu_mapping_destroy(self, context, mapping_uuid):
        with _session_for_write():
            query = model_query(context, models.InstanceCPUMapping)
            query = add_identity_filter(query, mapping_uuid)
            count = query.delete()
            if count != 1:
                raise exception.InstanceCPUMappingNotFound(uuid=mapping_uuid)
