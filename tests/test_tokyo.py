#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tokyo
----------------------------------

Tests for `tokyo` project.
"""
import os
import runpy
import sys
import unittest
from imp import reload
from unittest.mock import Mock, patch, call

TESTS_DIR = os.path.dirname(__file__)
sys.path.append(TESTS_DIR)
ROOT_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(ROOT_DIR)

import config_test


def resp_generator(responses):
    for response in responses:
        if isinstance(response, BaseException):
            raise response
        else:
            yield response


def _slack_api_call_builder(mocks):
    def api_call_mock(*args, **kwargs):
        api_call = args[0]
        return mocks.get(api_call, Mock(name=api_call))(*args[1:], **kwargs)
    return api_call_mock


class TestPlatforms(unittest.TestCase):

    def setUp(self):
        """setUp runs before every test is executed.

        Mock godzillops.Chat class and ovrride config.py loaded by tokyo's main.py
        """
        # == Override existing config with test config ==
        self.config = reload(config_test)
        self.logging_mock = Mock(name='logging')
        self.modules_patch = patch.dict('sys.modules', {'config': self.config,
                                                        'logging': self.logging_mock,
                                                        'time': Mock()})
        self.modules_patch.start()

        # Used in slack test methods
        self.user = 'U87654321'
        self.channel = 'C13934'

    def tearDown(self):
        self.modules_patch.stop()

    def test_000_text_chat_successful(self):
        """Make sure we initialized a text Chat platform without exception."""
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(return_value=resp_generator(('Huh?',)))
        _builtins = {
            'print': Mock(),
            'input': Mock(side_effect=['Hey', 'Bye', EOFError('FIN')])
        }

        with patch('godzillops.Chat', gz_chat_mock):
            with patch.multiple('builtins', **_builtins):
                runpy.run_module('main', run_name='__main__')

        self.assertTrue(gz_chat_mock.called)
        gz_chat_mock().respond.assert_has_calls((call('Hey'), call('Bye')))
        _builtins['print'].assert_has_calls((call('Huh?'), call('Exiting...')))

    def test_001_text_chat_respond_exception(self):
        """Force an exception on respond in text Chat platform."""
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(side_effect=[resp_generator(('Huh?',)), resp_generator((ValueError('BOOM'),))])
        _builtins = {
            'print': Mock(),
            'input': Mock(side_effect=['Hey', 'Bye', EOFError('FIN')])
        }

        with patch('godzillops.Chat', gz_chat_mock):
            with patch.multiple('builtins', **_builtins):
                runpy.run_module('main', run_name='__main__')

        self.assertTrue(gz_chat_mock.called)
        gz_chat_mock().respond.assert_has_calls((call('Hey'), call('Bye')))
        _builtins['print'].assert_has_calls((call('Huh?'), call('An error occurred - check the logs.'), call('Exiting...')))
        self.logging_mock.exception.assert_called_with("Error generated responding to < Bye >.")
        self.assertTrue(gz_chat_mock().cancel.called)

    def test_002_slack_chat_successful(self):
        """Make sure we initialized a slack Chat platform without exception."""
        self.config.PLATFORM = "slack"

        slack_mock = Mock(name='slackclient')
        self.user = 'U87654321'
        slack_events = [[{'type': 'message', 'text': 'What?', 'channel': self.channel, 'user': self.user}],
                        [{'type': 'message', 'text': 'Huh?', 'channel': self.channel, 'user': self.config.SLACK_USER}],
                        [{'type': 'message', 'text': 'Okay?', 'channel': self.channel, 'user': self.user}],
                        KeyboardInterrupt()]
        slack_mock().rtm_read = Mock(side_effect=slack_events)
        user_info = {'ok': True, 'user': {'id': self.user, 'tz': 'America/Chicago',
                                          'tz_label': 'Central Daylight Time', 'tz_offset': -18000}}
        user_info_mock = Mock(name='users.info', return_value=user_info)
        post_message_mock = Mock(name='chat.postMessage')
        slack_mock().api_call = _slack_api_call_builder({'users.info': user_info_mock, 'chat.postMessage': post_message_mock})
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(return_value=resp_generator(('Huh?',)))

        with patch('slackclient.SlackClient', slack_mock):
            with patch('godzillops.Chat', gz_chat_mock):
                runpy.run_module('main', run_name='__main__')

        self.assertTrue(gz_chat_mock.called)
        slack_mock.assert_called_with(self.config.SLACK_TOKEN)
        self.assertTrue(slack_mock().rtm_connect.called)
        self.assertTrue(slack_mock().rtm_read.called)
        user_info_mock.assert_called_with(user=self.user)
        gz_chat_mock().respond.assert_has_calls((call('What?', context={'tz_label': 'Central Daylight Time', 'tz': 'America/Chicago', 'user': self.user, 'tz_offset': -18000}),
                                                 call('Okay?', context={'tz_label': 'Central Daylight Time', 'tz': 'America/Chicago', 'user': self.user, 'tz_offset': -18000})))

    def test_003_slack_chat_invalid_token(self):
        """Make sure slack Chat platform dies with an invalid token."""
        self.config.PLATFORM = "slack"
        self.config.SLACK_TOKEN = "yourtoken"

        slack_mock = Mock(name='slackclient')
        gz_chat_mock = Mock(name='godzillops.Chat')

        with patch('slackclient.SlackClient', slack_mock):
            with patch('godzillops.Chat', gz_chat_mock):
                with self.assertRaises(SystemExit):
                    runpy.run_module('main', run_name='__main__')

        self.assertTrue(gz_chat_mock.called)
        self.assertFalse(slack_mock.called)

    def test_004_slack_get_user_info_dies(self):
        """Handle get_user_info api call death in slack Chat platform."""
        self.config.PLATFORM = "slack"

        slack_mock = Mock(name='slackclient')
        self.user = 'U87654321'
        user_not_found = 'User {} not found'.format(self.user)
        slack_events = [[{'type': 'message', 'text': 'What?', 'channel': self.channel, 'user': self.user}]]
        slack_mock().rtm_read = Mock(side_effect=slack_events)
        user_info = {'ok': False, 'user_not_found': user_not_found}
        user_info_mock = Mock(name='users.info', return_value=user_info)
        post_message_mock = Mock(name='chat.postMessage')
        slack_mock().api_call = _slack_api_call_builder({'users.info': user_info_mock, 'chat.postMessage': post_message_mock})
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(return_value=resp_generator(('Huh?',)))

        with patch('slackclient.SlackClient', slack_mock):
            with patch('godzillops.Chat', gz_chat_mock):
                with self.assertRaises(ValueError) as cxt:
                    runpy.run_module('main', run_name='__main__')

        self.assertTrue(gz_chat_mock.called)
        slack_mock.assert_called_with(self.config.SLACK_TOKEN)
        self.assertTrue(slack_mock().rtm_connect.called)
        self.assertTrue(slack_mock().rtm_read.called)
        user_info_mock.assert_called_with(user=self.user)
        self.assertEqual(str(cxt.exception), 'Getting user information died: {}'.format(user_info))
        self.assertFalse(gz_chat_mock().respond.called)
        self.assertFalse(post_message_mock.called)

    def test_005_slack_respond_exception(self):
        """Make sure we initialized a slack Chat platform without exception."""
        self.config.PLATFORM = "slack"

        slack_mock = Mock(name='slackclient')
        slack_events = [[{'type': 'message', 'text': 'What?', 'channel': self.channel, 'user': self.user}],
                        [{'type': 'message', 'text': 'Huh?', 'channel': self.channel, 'user': self.config.SLACK_USER}],
                        [{'type': 'message', 'text': 'Okay?', 'channel': self.channel, 'user': self.user}],
                        [{'type': 'message', 'text': 'An error occurred - check the logs.', 'channel': self.channel, 'user': self.config.SLACK_USER}],
                        KeyboardInterrupt()]
        slack_mock().rtm_read = Mock(side_effect=slack_events)
        user_info = {'ok': True, 'user': {'id': self.user, 'tz': 'America/Chicago',
                                          'tz_label': 'Central Daylight Time', 'tz_offset': -18000}}
        user_info_mock = Mock(name='users.info', return_value=user_info)
        post_message_mock = Mock(name='chat.postMessage')
        slack_mock().api_call = _slack_api_call_builder({'users.info': user_info_mock, 'chat.postMessage': post_message_mock})
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(side_effect=[resp_generator(('Huh?',)), resp_generator((ValueError('BOOM'),))])

        with patch('slackclient.SlackClient', slack_mock):
            with patch('godzillops.Chat', gz_chat_mock):
                runpy.run_module('main', run_name='__main__')

        self.assertTrue(gz_chat_mock.called)
        slack_mock.assert_called_with(self.config.SLACK_TOKEN)
        self.assertTrue(slack_mock().rtm_connect.called)
        self.assertTrue(slack_mock().rtm_read.called)
        user_info_mock.assert_called_with(user=self.user)
        gz_chat_mock().respond.assert_has_calls((call('What?', context={'tz_label': 'Central Daylight Time', 'tz': 'America/Chicago', 'user': self.user, 'tz_offset': -18000}),
                                                 call('Okay?', context={'tz_label': 'Central Daylight Time', 'tz': 'America/Chicago', 'user': self.user, 'tz_offset': -18000})))
        post_message_mock.assert_has_calls((call(text='Huh?', channel=self.channel, as_user=True),
                                            call(text='An error occurred - check the logs.', channel=self.channel, as_user=True)))
        self.logging_mock.exception.assert_called_with("Error generated responding to < Okay? >.")
        self.assertTrue(gz_chat_mock().cancel.called)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
