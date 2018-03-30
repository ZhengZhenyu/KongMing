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

from oslo_config import cfg


executor_opts = [
    cfg.StrOpt('executor_trigger_metadata_key',
               default='kongming-vcpu-pinning',
               help='The key to be used to informing kongming for '
                    'vcpu pinning')
]


def register_opts(conf):
    conf.register_opts(
        executor_opts, group="executor")
