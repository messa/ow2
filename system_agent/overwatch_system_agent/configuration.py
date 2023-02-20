from pathlib import Path
from yaml import safe_load as yaml_load


class Configuration:

    default_sleep_interval = 15 # in seconds

    def __init__(self, cfg_path):
        cfg_path = Path(cfg_path).resolve()
        cfg_dir = cfg_path.parent
        cfg = yaml_load(cfg_path.read_text())['overwatch_system_agent']
        self.report_url = cfg['report_url']
        self.report_token = cfg['report_token']
        self.label = cfg.get('label') or {}
        self.sleep_interval = float(cfg.get('sleep_interval') or default_sleep_interval)
        self.log_file_path = None
        if cfg.get('log'):
            if cfg['log'].get('file'):
                self.log_file_path = cfg_dir / cfg['log']['file']
