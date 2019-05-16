from logging import getLogger
from pathlib import Path
from yaml import safe_load as yaml_load


logger = getLogger(__name__)


class Configuration:

    def __init__(self, cfg_path):
        cfg_path = Path(cfg_path).resolve()
        cfg_dir = cfg_path.parent
        logger.debug('Reading configuration from %s', cfg_path)
        cfg = yaml_load(cfg_path.read_text())['overwatch_hub']
        get_list = lambda key: cfg.get(key) or []
        self.http_interface = HTTPInterface(cfg.get('http_interface') or {})
        self.mongodb = MongoDB(cfg['mongodb'], cfg_dir)
        self.alert_webhooks = [AlertWebhook(x) for x in get_list('alert_webhooks')]


class HTTPInterface:

    def __init__(self, cfg):
        self.bind_host = cfg.get('bind_host') or ''
        self.bind_port = int(cfg.get('bind_port') or cfg.get('port') or 8485)


class MongoDB:

    def __init__(self, cfg, cfg_dir):
        self.uri = cfg['uri']
        if not self.uri.startswith('mongodb://'):
            raise Exception('mongodb uri does not start with "mongodb://"')
        self.ssl_ca_cert_file = None
        if cfg.get('ssl') and cfg['ssl'].get('ca_cert_file'):
            self.ssl_ca_cert_file = cfg_dir / cfg['ssl']['ca_cert_file']


class AlertWebhook:

    def __init__(self, cfg):
        self.url = cfg['url']
        self.format = cfg.get('format') or 'text'
        self.authorization_header = cfg.get('authorization_header')
