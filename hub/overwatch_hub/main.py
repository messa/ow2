from argparse import ArgumentParser
from logging import getLogger


logger = getLogger(__name__)


def hub_main():
    p = ArgumentParser()
    p.add_argument('--conf', '-f', help='path to configuration file')
    args = p.parse_args()
    setup_logging()


def setup_logging():
    from logging import DEBUG, basicConfig
    basicConfig(
        format='%(asctime)s %(name)s %(levelname)5s: %(message)',
        level=DEBUG)
