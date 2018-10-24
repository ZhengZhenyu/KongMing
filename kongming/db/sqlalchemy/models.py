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

"""SQLAlchemy models for cpu allocation service."""

from oslo_db import options as db_options
from oslo_db.sqlalchemy import models
import six.moves.urllib.parse as urlparse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index
from sqlalchemy import Text
from sqlalchemy import schema

from kongming.common import paths
from kongming.conf import CONF


_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('kongming.sqlite')
db_options.set_defaults(CONF, connection=_DEFAULT_SQL_CONNECTION)


def table_args():
    engine_name = urlparse.urlparse(CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class KongmingBase(models.TimestampMixin, models.ModelBase):
    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d


Base = declarative_base(cls=KongmingBase)


class InstanceCPUMapping(Base):
    """Represents the InstanceCPUMapping."""

    __tablename__ = 'instance_cpu_mappings'
    __table_args__ = (
        schema.UniqueConstraint('instance_uuid',
                                name='uniq_mappings0instance_uuid'),
        table_args()
    )

    id = Column(Integer, primary_key=True)
    instance_uuid = Column(String(36), nullable=False)
    project_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    host = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    cpu_mappings = Column(String(255), nullable=True)


class Instance(Base):
    """Represents the Instance."""

    __tablename__ = 'instances'
    __table_args__ = (
        schema.UniqueConstraint('uuid',
                                name='uniq_instances0uuid'),
        table_args()
    )

    uuid = Column(String(36), primary_key=True, nullable=False)
    host = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    cpu_mappings = Column(Text, nullable=True)


class Hosts(Base):
    """Represents the Host."""

    __tablename__ = 'hosts'
    __table_args__ = (
        schema.UniqueConstraint('host_name',
                                name='uniq_hosts0host_name'),
        table_args()
    )

    id = Column(Integer, primary_key=True)
    host_name = Column(String(255), nullable=True)
    cpu_topology = Column(Text, nullable=True)
