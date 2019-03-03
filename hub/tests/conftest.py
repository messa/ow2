import os
from pathlib import Path
from pytest import fixture


here = Path(__file__).resolve().parent

on_CI = bool(os.environ.get('CI'))
