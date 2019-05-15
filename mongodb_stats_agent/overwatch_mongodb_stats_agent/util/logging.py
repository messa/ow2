from logging import Formatter
from logging import getLogger as _getLogger


default_format = '%(asctime)s %(name)-20s %(levelname)5s: %(message)s'


def get_logger(name):
    logger = _getLogger(name)
    return logger


class CustomFormatter (Formatter):

    def __init__(self, fmt=None, style='%', strip_name_prefix=None, **kwargs):
        if not fmt:
            fmt = default_format
            style = '%'
        super().__init__(fmt, style=style, **kwargs)
        self.strip_name_prefix = strip_name_prefix

    def formatMessage(self, record):
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
