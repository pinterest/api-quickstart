import unittest
from unittest import mock

from src.v5.oauth_scope import Scope, lookup_scope


class OAuthScopeTest(unittest.TestCase):
    @mock.patch("builtins.print")
    def test_lookup(self, mock_print):
        with self.assertRaises(SystemExit) as sysex:
            lookup_scope("help")
        self.assertEqual(0, sysex.exception.code)
        # print should be called once with the help message
        mock_print.assert_called_once()
        mock_print.reset_mock()

        with self.assertRaises(SystemExit) as sysex:
            lookup_scope("oops")
        self.assertEqual(1, sysex.exception.code)
        # print should be called once with an error message and
        # a second time with the help message
        mock_print.assert_has_calls([mock.call("Invalid scope:", "oops"), mock.ANY])
        mock_print.reset_mock()

        self.assertEqual(Scope.READ_BOARDS, lookup_scope("rEAd_BoardS"))
        self.assertEqual(Scope.READ_BOARDS, lookup_scope("bOARds:reAd"))
        mock_print.assert_not_called()
