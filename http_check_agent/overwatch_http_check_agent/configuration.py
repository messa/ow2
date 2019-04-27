from pathlib import Path
from yaml import safe_load as yaml_load


class Configuration:

    def __init__(self, cfg_path):
        cfg_path = Path(cfg_path).resolve()
        cfg_dir = cfg_path.parent
        cfg = yaml_load(cfg_path.read_text())['overwatch_http_check_agent']
        self.report_url = cfg['report_url']
        self.report_token = cfg['report_token']
