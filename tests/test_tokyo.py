#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tokyo
----------------------------------

Tests for `tokyo` project.
"""
import os
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

        Make sure that we create and mock all API pieces - i.e. Google API objects & Trello urllib calls.
        """
        import config_test
        self.config = config_test
        # First, we need to create our per-test mocks

        # == Override existing config with test config ==
        self.config_patch = patch.dict('sys.modules', {'config': self.config})
        self.config_patch.start()
        import main as tokyo

        # == Godzillops Chat Class ==
        self.gz_chat_mock = Mock(name='godzillops.Chat')
        self.gz_chat_responses = ()
        self.gz_chat_mock().respond = Mock(return_value=self.gz_chat_responses)
        self.gz_patch = patch.object(tokyo.platform, 'Chat', self.gz_chat_mock)
        self.gz_patch.start()

        # == Other Functions ==
        self.other_patch = patch.object(tokyo.platform, 'print')
        self.other_patch.start()

        self.platform = tokyo.platform

    def tearDown(self):
        self.other_patch.stop()
        self.gz_patch.stop()
        self.config_patch.stop()

    def test_000_text_chat_successful(self):
        """Make sure we initialized a text Chat platform without exception."""
        self.config.PLATFORM = "text"
        with patch.object(self.platform, 'input', Mock(side_effect=['Hey', 'Bye', EOFError('FIN')])):
            self.platform.main(self.config)



if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
