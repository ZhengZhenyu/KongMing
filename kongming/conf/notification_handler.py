from oslo_config import cfg


notification_handler_opts = [
    cfg.IntOpt('workers',
               default=1,
               min=1,
               help='Number of workers for notification service. A single '
               'notification agent is enabled by default.'),
    cfg.StrOpt('notifications_pool',
               default='kongming-notification-handler',
               help='Use an oslo.messaging pool, which can be an alternative '
               'to multiple topics. ')
]


def register_opts(conf):
    conf.register_opts(
        notification_handler_opts, group="notification_handler")
