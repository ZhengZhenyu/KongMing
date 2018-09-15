# Copyright 2018 Zhenyu Zheng <zheng.zhenyu@outlook.com>
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

from kongming.agent import manager as agent_manager

LOG = logging.getLogger(__name__)

SUPPORTED_ENVENTS = [
    'instance.create.end', 'instance.instance_metadata_update']


class NotificationEndpoint(object):
    def __init__(self):
        self.agent = agent_manager.AgentManager()

    def _process_event(self, ctxt, publisher_id, event_type, payload,
                       metadata, priority):
        self.agent.execute_notifications(payload)

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        event_type_l = event_type.lower()
        if event_type_l in SUPPORTED_ENVENTS and \
                payload['nova_object.data']['host'] == self.agent.host:
            self._process_event(ctxt, publisher_id, event_type,
                                payload, metadata, 'INFO')

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        self._process_event(ctxt, publisher_id, event_type, payload, metadata,
                            'ERROR')

