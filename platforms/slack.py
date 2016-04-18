import logging
import sys
import time

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
                response_required = all([event['type'] == 'message',
                                         event.get('text'),
                                         event.get('user') != config.SLACK_USER])

                if response_required:
                    logging.debug(event)
                    responses = gz_chat.respond(event['text'], context=event)
                    for response in responses:
                        sc.api_call(
                            "chat.postMessage", channel=event['channel'], as_user=True,
                            text=response
                        )
            time.sleep(1)
