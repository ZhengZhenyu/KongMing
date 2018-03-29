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
