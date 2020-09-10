import unittest
import tempfile
from pathlib import Path
import os

from ..log import Log


class TestInit(unittest.TestCase):
    def test_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = Path(tmpdir, "foobar")
            instance = Log(fp)

            self.assertTrue(fp.exists())

    def test_file_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = Path(tmpdir, "foobar")
            instance = Log(fp)

            self.assertTrue(os.access(fp, os.R_OK))
            self.assertTrue(os.access(fp, os.W_OK))

    def test_file_is_read(self):
        fp = (
            Path("worklog", "tests", "snapshots", "session_simple.csv")
            .absolute()
            .as_posix()
        )
        instance = Log(fp)
        self.assertFalse(instance._log_df.empty)

