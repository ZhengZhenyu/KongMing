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

from oslo_log import log as logging
import oslo_messaging
from oslo_service import service as os_service

from kongming.conf import CONF
from kongming.executor import manager as exe_manager

LOG = logging.getLogger(__name__)


class NotificationEndpoint(object):
    def __init__(self):
        self.executor = exe_manager.ExecutorManager()

    def _process_event(self, ctxt, publisher_id, event_type, payload,
                       metadata, priority):
        self.executor.execute(payload)

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        event_type_l = event_type.lower()
        if event_type_l == 'instance.create.end' and \
                payload['nova_object.data']['host'] == self.executor.hostname:
            self._process_event(ctxt, publisher_id, event_type,
                                payload, metadata, 'INFO')

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        self._process_event(ctxt, publisher_id, event_type, payload, metadata,
                            'ERROR')


class ListenerService(os_service.Service):
    def __init__(self, *args, **kwargs):
        super(ListenerService, self).__init__(*args, **kwargs)
        self.listener = None

    def start(self):
        super(ListenerService, self).start()
        transport = oslo_messaging.get_notification_transport(CONF)
        targets = [
            oslo_messaging.Target(topic='versioned_notifications',
                                  exchange='nova')
        ]
        endpoints = [
            NotificationEndpoint()
        ]
        self.listener = oslo_messaging.get_notification_listener(
            transport,
            targets,
            endpoints,
            executor='threading',
            pool=CONF.notifications_pool.notifications_pool)

        self.listener.start()

    def stop(self):
        self.listener.stop()
        self.listener.wait()
        super(ListenerService, self).stop()
