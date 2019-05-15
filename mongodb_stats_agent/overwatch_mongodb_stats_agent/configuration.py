from datetime import timedelta
from pathlib import Path
from yaml import safe_load as yaml_load


class Configuration:

    def __init__(self, cfg_path):
        cfg_path = Path(cfg_path).resolve()
        cfg_dir = cfg_path.parent
        cfg = yaml_load(cfg_path.read_text())['overwatch_ping_agent']
        self.report_url = cfg['report_url']
        self.report_token = cfg['report_token']
        self.default_label = cfg.get('label') or {}
        self.targets = [Target(x) for x in cfg['targets']]


class Target:

    def __init__(self, cfg):
        self.address = cfg['address']
        self.label = cfg.get('label') or {}

    def __str__(self):
        return ' '.join('{}={!r}'.format(k, v) for k, v in self.__dict__.items())


def parse_interval(s):
    if not s:
        return None
    return timedelta(seconds=int(s))
