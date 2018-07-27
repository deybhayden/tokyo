#!/usr/bin/env python
import logging
import sys
from importlib import import_module

import config

# Set up Logger
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s", stream=sys.stdout, level=config.LOG_LEVEL
)
# Load Platform
platform = import_module("platforms." + config.PLATFORM)

if __name__ == "__main__":
    # Launch platform with config
    platform.main(config)
