# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestReport::test_report_with_tasks 1'] = '''Aggregated by month:
--------------------
                Date           Total time
             2020-01             09:00:00
             2020-02             09:00:00

Aggregated by week:
-------------------
                Date           Total time
          2020-01-05             09:00:00
          2020-01-12             00:00:00
          2020-01-19             00:00:00
          2020-01-26             00:00:00
          2020-02-02             09:00:00

Aggregated by day:
------------------
                Date           Total time
          2020-01-01             09:00:00
          2020-02-01             09:00:00

Aggregated by tasks:
--------------------
           Task name           Total time
               task1             09:50:00
               task2             17:30:00

'''

snapshots['TestReport::test_report_with_tasks_and_autobreak 1'] = '''Aggregated by month:
--------------------
                Date           Total time                Break        Bookable time
             2020-01             09:00:00             01:00:00             08:00:00
             2020-02             09:00:00             01:00:00             08:00:00

Aggregated by week:
-------------------
                Date           Total time                Break        Bookable time
          2020-01-05             09:00:00             01:00:00             08:00:00
          2020-01-12             00:00:00             00:00:00             00:00:00
          2020-01-19             00:00:00             00:00:00             00:00:00
          2020-01-26             00:00:00             00:00:00             00:00:00
          2020-02-02             09:00:00             01:00:00             08:00:00

Aggregated by day:
------------------
                Date           Total time                Break        Bookable time
          2020-01-01             09:00:00             01:00:00             08:00:00
          2020-02-01             09:00:00             01:00:00             08:00:00

Aggregated by tasks:
--------------------
           Task name           Total time
               task1             09:50:00
               task2             17:30:00

'''
