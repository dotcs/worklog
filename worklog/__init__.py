from datetime import datetime, timedelta, timezone
import logging
import configparser
import pathlib
import os
import sys
import argparse

logger = logging.getLogger(__name__)

CONFIG_FILES = [
    os.path.expanduser('~/.config/worklog/config'),
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.cfg'),
]

class WorkLogEntry(object):

    @staticmethod
    def now(type_: str, value: str):
        now = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
        return WorkLogEntry(now, type_, value)

    _type = None
    _value = None
    _timestamp = None

    def __init__(self, timestamp, type_: str, value: str):
        self._timestamp = timestamp
        self._type = type_
        self._value = value
    
    def __str__(self):
        return '|'.join([self._timestamp.isoformat(), self._type, self._value])

class WorkLogEntries(object):
    _entries = []
    _separator = '|'

    def parse(self, fp):
        with open(fp) as f:
            for i, line in enumerate(f.readlines()):
                if len(line.strip()) == 0:
                    continue
                cols = line.strip().split(self._separator)
                cols[0] = datetime.fromisoformat(cols[0])
                entry = WorkLogEntry(*cols)
                self._entries.append(entry)

    def add(self, entry):
        self._entries.append(entry)

    def persist(self, fp, mode='append'):
        open_mode = 'w' if mode == 'overwrite' else 'a'
        with open(fp, open_mode) as f:
            val = str(self)
            if len(val) == 0:
                f.write('')
            else:
                f.write(str(self) + '\n')

    def undo(self):
        self._entries = self._entries[:-1]

    def __str__(self):
        val = ''
        for item in self._entries:
            val += self._separator.join([item._timestamp.isoformat(), item._type, item._value]) + '\n'
        return val.strip()


def _get_ts_formatted():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

def clock_in_out(fp, type_):
    logger.debug(str(entries))
    

def dispatch(cfg, cli_args):
    worklog_fp = os.path.expanduser(cfg.get('worklog', 'path'))
    logger.debug(worklog_fp)

    if cli_args.level1 == 'clock':
        if cli_args.type in ['in', 'out']:
            entries = WorkLogEntries()
            entries.add(WorkLogEntry.now('in_out', cli_args.type))
            entries.persist(worklog_fp, mode='append')
        elif cli_args.type == 'undo':
            entries = WorkLogEntries()
            entries.parse(worklog_fp)
            entries.undo()
            entries.persist(worklog_fp, mode='overwrite')
    elif cli_args.level1 == 'status':
        entries = WorkLogEntries()
        entries.parse(worklog_fp)
        logger.debug(entries)

def run():
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser('WorkLog')
    subparsers = parser.add_subparsers(dest='level1')

    clock_parser = subparsers.add_parser('clock')
    status_parser = subparsers.add_parser('status')

    clock_parser.add_argument('type', choices=['in', 'out', 'undo'], help='Writes a clock-in or clock-out entry to the logfile')

    parser.add_argument('-v', '--verbose', dest='verbosity', action='count', default=0)
    log_levels = [logging.FATAL, logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    cli_args = parser.parse_args()
    logger.setLevel(log_levels[min(cli_args.verbosity, len(log_levels) - 1)])

    logger.debug(cli_args)
    
    logger.debug(CONFIG_FILES)

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILES)

    dispatch(cfg, cli_args)


if __name__ == "__main__":
    run()