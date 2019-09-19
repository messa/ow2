raise_error = object()
# ^^^ this is a special value, which when passed as a default value to a get function,
# will cause to raise exception instead of returning default value


class InitialConnectionError (Exception):
    log_traceback = False


class NotFoundError (Exception):
    pass


class AlertNotFoundError (NotFoundError):

    def __init__(self, alert_id):
        super().__init__(f'Alert id {alert_id} not found')


class AccessTokenNotFoundError (NotFoundError):
    pass
