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

import sys

from oslo_config import cfg
from oslo_service import service as os_service

from kongming.common import service
from kongming.notification_handler import manager


CONF = cfg.CONF


def main():
    service.prepare_service(sys.argv)
    launcher = os_service.ProcessLauncher(CONF)
    launcher.launch_service(
        manager.ListenerService(),
        workers=CONF.notification_handler.workers)
    launcher.wait()

if __name__ == "__main__":
    main()
