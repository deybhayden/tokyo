import logging
import sys
import time

from slackclient import SlackClient
from godzillops.godzillops import Chat


def main(config):
    gz_chat = Chat(config)
    if not config.SLACK_TOKEN or config.SLACK_TOKEN == 'yourtoken':
        sys.exit('Exiting... SLACK_TOKEN was empty or not updated from the default in config.py.')

    sc = SlackClient(config.SLACK_TOKEN)

    try:
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
                        text = event.pop('text')
                        responses = gz_chat.respond(text, context=event)
                        try:
                            for response in responses:
                                sc.api_call(
                                    "chat.postMessage", channel=event['channel'], as_user=True,
                                    text=response
                                )
                        except:
                            # clear any action started
                            gz_chat.cancel()
                            logging.exception("Error generated responding to < {} >.".format(text))
                            sc.api_call(
                                "chat.postMessage", channel=event['channel'], as_user=True,
                                text="An error occurred - check the logs."
                            )
                time.sleep(1)
    except (KeyboardInterrupt):
        logging.info("Exiting...")
