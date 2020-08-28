import unittest
from unittest.mock import patch

from worklog.utils.pager import get_pager


class TestPager(unittest.TestCase):
    @patch("os.getenv")
    @patch("shutil.which")
    def test_get_pager_no_less_and_env_unset(self, mock_which, mock_getenv):
        mock_which.side_effect = ["/path/to/more", None]
        mock_getenv.side_effect = lambda _, default_value: default_value

        actual = get_pager()
        expected = "/path/to/more"

        self.assertEqual(actual, expected)

    @patch("os.getenv")
    @patch("shutil.which")
    def test_get_pager_no_less_and_env_set(self, mock_which, mock_getenv):
        mock_which.side_effect = ["/path/to/more", None]
        mock_getenv.return_value = "/path/to/less"

        actual = get_pager()
        expected = "/path/to/less"

        self.assertEqual(actual, expected)

    @patch("os.getenv")
    @patch("shutil.which")
    def test_get_pager_has_less_and_env_unset(self, mock_which, mock_getenv):
        mock_which.side_effect = ["/path/to/more", "/path/to/less"]
        mock_getenv.side_effect = lambda _, default_value: default_value

        actual = get_pager()
        expected = "/path/to/less"

        self.assertEqual(actual, expected)
