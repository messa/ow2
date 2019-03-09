from pathlib import Path
from yaml import safe_load as yaml_load


class Configuration:

    def __init__(self, cfg_path):
        cfg_path = Path(cfg_path).resolve()
        cfg_dir = cfg_path.parent
        cfg = yaml_load(cfg_path.read_text())['overwatch_hub']
        self.port = int(cfg.get('port') or 8485)
        self.mongodb = MongoDB(cfg['mongodb'])


class MongoDB:

    def __init__(self, cfg):
        self.uri = cfg['uri']
        if not self.uri.startswith('mongodb://'):
            raise Exception('mongodb uri does not start with "mongodb://"')
