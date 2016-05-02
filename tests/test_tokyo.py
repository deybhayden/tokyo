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
from unittest.mock import Mock, patch

TESTS_DIR = os.path.dirname(__file__)
sys.path.append(TESTS_DIR)
ROOT_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(ROOT_DIR)


class TestText(unittest.TestCase):

    def setUp(self):
        """setUp runs before every test is executed.

        Mock godzillops.Chat class and ovrride config.py loaded by tokyo's main.py
        """
        import config_test
        self.config = config_test
        # First, we need to create our per-test mocks

        # == Override existing config with test config ==
        self.config_patch = patch.dict('sys.modules', {'config': self.config})
        self.config_patch.start()

        # == Godzillops Chat Class ==
        self.gz_chat_mock = Mock(name='godzillops.Chat')
        self.gz_chat_responses = ()
        self.gz_chat_mock().respond = Mock(return_value=self.gz_chat_responses)
        self.gz_patch = patch('godzillops.Chat', self.gz_chat_mock)
        self.gz_patch.start()

    def tearDown(self):
        self.gz_patch.stop()
        self.config_patch.stop()

    def test_000_text_chat_successful(self):
        """Make sure we initialized a text Chat platform without exception."""
        self.config.PLATFORM = "text"
        mocks = {
            'print': Mock(),
            'input': Mock(side_effect=['Hey', 'Bye', EOFError('FIN')])
        }
        with patch.multiple('platforms.text', **mocks):
            runpy.run_module('main', run_name='__main__')
            mocks['print'].assert_called_with('Exiting...')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
