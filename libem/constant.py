import os
import sys
import yaml
import logging

LIBEM_DIR = os.path.join(os.path.expanduser("~"), ".libem")
LIBEM_CONFIG_FILE = os.path.join(LIBEM_DIR, "config.yaml")
LIBEM_SOURCE = os.path.dirname(os.path.abspath(__file__))

try:
    with open(LIBEM_CONFIG_FILE, "r") as f:
        LIBEM_CONFIG = yaml.load(f, Loader=yaml.SafeLoader)
except FileNotFoundError:
    print(f"Config file not found at {LIBEM_CONFIG_FILE}")
    sys.exit(1)

LIBEM_LOG_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "logs")
LIBEM_DO_LOG = bool(int(os.environ.get("LIBEM_DO_LOG", False)))
# DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40
LIBEM_LOG_LEVEL = \
    int(os.environ.get("LIBEM_LOG_LEVEL", logging.INFO))
LIBEM_3RD_PARTY_LOG_LEVEL = \
    os.environ.get("LIBEM_3RD_PARTY_LOG_LEVEL", logging.WARNING)

LIBEM_SEED = int(os.environ.get("LIBEM_SEED", 42))
