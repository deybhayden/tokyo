import logging
import sys
import time
from functools import lru_cache

from slackclient import SlackClient
from godzillops import Chat


@lru_cache(maxsize=32)
def get_user_info(sc, user_id):
    """Cached `users.info` API calls to slack

    We use the user info JSON so we can know a user's timezone information.

    Args:
        sc (SlackClient): A RTM connected slack client used for making API calls.
        user_id (str): A slack user id to get more information about.
    Returns:
        dict: If response was successful, a dictionary containing a User ID's name & timezone.
    """
    response = sc.api_call('users.info', user=user_id)
    if response['ok']:
        return response['user']
    else:
        raise ValueError('Getting user information died: ' + str(response))


@lru_cache(maxsize=32)
def open_im_channel(sc, user_id):
    """Cached `im.open` API call to slack for a user

    Use the current bot's token to get a list of all IM channels we have access to.

    Args:
        sc (SlackClient): A RTM connected slack client used for making API calls
        user_id (str): A slack user id to open a DM channel with.
    Returns:
        str: If response was successful, the direct message channel id for a user & the bot.
    """
    response = sc.api_call('im.open', user=user_id)
    if response['ok']:
        return response['channel']['id']
    else:
        raise ValueError('Opening im channel died: ' + str(response))


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
                        user = get_user_info(sc, event['user'])
                        text = event.pop('text')
                        responses = gz_chat.respond(text, context={'user': user})
                        try:
                            for response in responses:
                                if isinstance(response, str):
                                    # Text is just feedback/chat from GZ
                                    sc.api_call(
                                        "chat.postMessage", channel=event['channel'], as_user=True,
                                        text=response
                                    )
                                elif isinstance(response, dict):
                                    # A dictionary represents a completed action (successful or failed)
                                    if response['admin_action_complete']:
                                        other_admins = [a for a in config.ADMINS if a != user['id']]
                                        for admin_id in other_admins:
                                            logging.info("Admin action completed - informing admin user {}".format(admin_id))
                                            dm_channel = open_im_channel(sc, admin_id)
                                            sc.api_call(
                                                "chat.postMessage", channel=dm_channel, as_user=True,
                                                text=response['message']
                                            )
                        except:
                            logging.exception("Error generated responding to < {} >.".format(text))
                            sc.api_call(
                                "chat.postMessage", channel=event['channel'], as_user=True,
                                text="An error occurred - check the logs. Reinitializing GZ."
                            )
                            gz_chat = Chat(config)
                time.sleep(1)
        else:
            logging.error('Connecting to Slack failed... make sure the token is valid.')
    except (KeyboardInterrupt):
        logging.info("Exiting...")
