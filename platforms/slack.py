import logging
import sys

from slackclient import SlackClient
from godzillops.godzillops import Chat

gz_chat = Chat()

def main(config):
    if not config.SLACK_TOKEN or config.SLACK_TOKEN == 'yourtoken':
        sys.exit('Exiting... SLACK_TOKEN was empty or not updated from the default in config.py.')

    sc = SlackClient(config.SLACK_TOKEN)

    if sc.rtm_connect():
        logging.info("Listening for incoming messages...")

        while True:
            events = sc.rtm_read()
            for event in events:
                if event['type'] == 'message' and event['user'] != config.SLACK_USER:
                    logging.debug(event)
                    response = gz_chat.respond(event['text'], context=event)
                    sc.api_call(
                        "chat.postMessage", channel=event['channel'], as_user=True,
                        text=response
                    )
