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

from mogan.common.i18n import _

opts = [
    cfg.StrOpt(
                'compute_api_version',
                default='2.1',
                help='The compute API (micro)version, the provided '
                     'compute API (micro)version should be not smaller '
                     'than 2.1 and not larger than the max supported '
                     'Compute API microversion. The current supported '
                     'Compute API versions can be checked using: '
                     'nova version-list.')
]


def register_opts(conf):
    conf.register_opts(opts, group='nova')
