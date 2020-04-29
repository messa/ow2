import logging


log_format = '%(asctime)s [%(process)d] %(name)-30s %(levelname)5s: %(message)s'


def setup_logging(verbosity=0):
    from logging import DEBUG, Formatter, StreamHandler, getLogger
    getLogger().setLevel(DEBUG)
    h = StreamHandler()
    h.setLevel(get_level_by_verbosity(verbosity))
    h.setFormatter(Formatter(log_format))
    getLogger().addHandler(h)


def get_level_by_verbosity(verbosity):
    from logging import DEBUG, ERROR, INFO
    if not verbosity:
        return ERROR
    elif verbosity == 1:
        return INFO
    else:
        return DEBUG


def setup_log_file(log_file_path):
    from logging import DEBUG, Formatter, getLogger
    from logging.handlers import WatchedFileHandler
    if log_file_path:
        h = WatchedFileHandler(str(log_file_path))
        h.setLevel(DEBUG)
        h.setFormatter(Formatter(log_format))
        getLogger().addHandler(h)
