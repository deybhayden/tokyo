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
from unittest.mock import Mock, patch, call

TESTS_DIR = os.path.dirname(__file__)
sys.path.append(TESTS_DIR)
ROOT_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(ROOT_DIR)

def resp_generator(responses):
    for response in responses:
        if isinstance(response, BaseException):
            raise response
        else:
            yield response


class TestText(unittest.TestCase):

    def setUp(self):
        """setUp runs before every test is executed.

        Mock godzillops.Chat class and ovrride config.py loaded by tokyo's main.py
        """
        # First, we need to create our per-test mocks
        # == Override existing config with test config ==
        import config_test
        self.config = config_test
        self.logging_mock = Mock(name='logging')
        self.modules_patch = patch.dict('sys.modules', {'config': self.config, 'logging': self.logging_mock})
        self.modules_patch.start()

    def tearDown(self):
        self.modules_patch.stop()

    def test_000_text_chat_successful(self):
        """Make sure we initialized a text Chat platform without exception."""
        self.config.PLATFORM = "text"

        # Test specific mocks
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(return_value=resp_generator(('Huh?',)))
        _builtins = {
            'print': Mock(),
            'input': Mock(side_effect=['Hey', 'Bye', EOFError('FIN')])
        }

        with patch('godzillops.Chat', gz_chat_mock):
            with patch.multiple('builtins', **_builtins):
                runpy.run_module('main', run_name='__main__')

        gz_chat_mock().respond.assert_has_calls((call('Hey'), call('Bye')))
        _builtins['print'].assert_has_calls((call('Huh?'), call('Exiting...')))

    def test_001_text_chat_respond_exception(self):
        """Force an exception on respond in text Chat platform."""
        self.config.PLATFORM = "text"

        # Test specific mocks
        gz_chat_mock = Mock(name='godzillops.Chat')
        gz_chat_mock().respond = Mock(side_effect=[resp_generator(('Huh?',)), resp_generator((ValueError('BOOM'),))])
        _builtins = {
            'print': Mock(),
            'input': Mock(side_effect=['Hey', 'Bye', EOFError('FIN')])
        }

        with patch('godzillops.Chat', gz_chat_mock):
            with patch.multiple('builtins', **_builtins):
                runpy.run_module('main', run_name='__main__')

        gz_chat_mock().respond.assert_has_calls((call('Hey'), call('Bye')))
        _builtins['print'].assert_has_calls((call('Huh?'), call('An error occurred - check the logs.'), call('Exiting...')))
        self.logging_mock.exception.assert_called_with("Error generated responding to < Bye >.")
        self.assertTrue(gz_chat_mock().cancel.called)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
