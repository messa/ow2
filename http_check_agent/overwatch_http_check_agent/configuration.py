from datetime import timedelta
from pathlib import Path
from yaml import safe_load as yaml_load


class Configuration:

    def __init__(self, cfg_path):
        cfg_path = Path(cfg_path).resolve()
        cfg_dir = cfg_path.parent
        cfg = yaml_load(cfg_path.read_text())['overwatch_http_check_agent']
        self.report_url = cfg['report_url']
        self.report_token = cfg['report_token']
        self.default_interval = timedelta(seconds=30)
        self.default_label = {}
        self.duration_threshold = parse_interval(cfg.get('duration_threshold') or 5)
        self.targets = [Target(x) for x in cfg['targets']]


class Target:

    def __init__(self, cfg):
        self.url = cfg['url']
        self.interval = parse_interval(cfg.get('interval'))
        self.label = {}
        self.check_response_contains = cfg.get('check_response_contains')
        self.duration_threshold = parse_interval(cfg.get('duration_threshold'))

    def __str__(self):
        return ' '.join(f'{k}={v!r}' for k, v in self.__dict__.items())


def parse_interval(s):
    if not s:
        return None
    return timedelta(seconds=int(s))
