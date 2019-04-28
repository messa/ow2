class InitialConnectionError (Exception):
    log_traceback = False


class NotFoundError (Exception):
    pass


class AlertNotFoundError (NotFoundError):

    def __init__(self, alert_id):
        super().__init__(f'Alert id {alert_id} not found')
