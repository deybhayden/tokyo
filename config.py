import os
import logging

LOG_LEVEL = logging.WARNING
PLATFORM = "text"
SLACK_TOKEN = "yourtoken"
# Find the bot's Slack ID. You can obtain this using Slack's API tester - https://api.slack.com/methods/users.list
# or by inspecting the tokyo debug logs (by setting LOG_LEVEL = logging.DEBUG). It should look like U023BECGF.
SLACK_USER_ID = "U12345678"

if os.path.exists('config_private.py'):
    # Use config_private for your own personal settings - default to be git ignored.
    # Yup, intentionally using wildcard import to shadow the default values
    from config_private import *
