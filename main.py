#!/usr/bin/env python
from importlib import import_module

PLATFORM = 'text'

# Set platform appropriate environment variables
# import os
# os.environ['SLACK_TOKEN'] = 'blah'

if __name__ == '__main__':
    platform = import_module('platforms.'+PLATFORM)
    platform.main()
