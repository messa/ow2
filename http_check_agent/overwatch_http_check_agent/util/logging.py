from contextlib import contextmanager
from contextvars import ContextVar
from logging import Formatter
from logging import getLogger as _getLogger


default_format = '%(asctime)s [%(process)d] %(name)-20s %(levelname)5s: %(message)s'

log_context = ContextVar('log_context', default='')


@contextmanager
def add_log_context(s):
    v = log_context.get()
    token = log_context.set((v + ':' + s) if v else s)
    try:
        yield
    finally:
        log_context.reset(token)


def context_filter(record):
    if not getattr(record, 'log_context_added', False):
        cx = log_context.get()
        if cx:
            record.msg = '[{}] {}'.format(cx, record.msg)
        record.log_context_added = True
    return True


def get_logger(name):
    logger = _getLogger(name)
    logger.addFilter(context_filter)
    return logger


class CustomFormatter (Formatter):

    def __init__(self, fmt=None, style='%', strip_name_prefix=None, **kwargs):
        if not fmt:
            fmt = default_format
            style = '%'
        super().__init__(fmt, style=style, **kwargs)
        self.strip_name_prefix = strip_name_prefix

    def formatMessage(self, record):
        context_filter(record)
        orig_name = record.name
        try:
            record.name = self._process_record_name(record.name)
            return super().formatMessage(record)
        finally:
            record.name = orig_name

    def _process_record_name(self, name):
        if self.strip_name_prefix and name.startswith(self.strip_name_prefix):
            name = name[len(self.strip_name_prefix):]
        return name
