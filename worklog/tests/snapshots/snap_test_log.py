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

snapshots['TestStatus::test_tracking_on 1'] = '''Status         : Tracking on
Total time     : 23:59:59 (300%)
Remaining time : 00:00:00 (  0%)
Overtime       : 15:59:59 (800%)
Break Duration : 00:00:00
Touched tasks  : (1) [task1 (01:00:00)]
Active tasks   : (1) [task2]
'''

snapshots['TestStatus::test_tracking_off 1'] = '''Status         : Tracking off
Total time     : 02:00:00 ( 25%)
Remaining time : 06:00:00 ( 75%)
Overtime       : 00:00:00 (  0%)
Break Duration : 00:00:00
Touched tasks  : (2) [task1 (01:00:00), task2 (01:00:00)]
Active tasks   : (0) []
'''

snapshots['TestCommit::test_session_start 1'] = '''2020-01-01 00:00:00+00:00|2020-01-01 00:00:00+00:00|session|start|
'''

snapshots['TestCommit::test_session_start_and_stop 1'] = '''2020-01-01 00:00:00+00:00|2020-01-01 00:00:00+00:00|session|start|
2020-01-01 00:00:00+00:00|2020-01-01 01:00:00+00:00|session|stop|
'''

snapshots['TestCommit::test_session_and_task 1'] = '''2020-01-01 00:00:00+00:00|2020-01-01 00:00:00+00:00|session|start|
2020-01-01 00:00:00+00:00|2020-01-01 00:00:00+00:00|task|start|task1
2020-01-01 00:00:00+00:00|2020-01-01 01:00:00+00:00|task|stop|task1
2020-01-01 00:00:00+00:00|2020-01-01 01:00:00+00:00|session|stop|
'''

snapshots['TestCommit::test_stop_session_with_running_task_force 1'] = '''2020-01-01 00:00:00+00:00|2020-01-01 00:00:00+00:00|session|start|
2020-01-01 00:00:00+00:00|2020-01-01 00:00:00+00:00|task|start|task1
2020-01-01 00:00:00+00:00|2020-01-01 01:00:00+00:00|task|stop|task1
2020-01-01 00:00:00+00:00|2020-01-01 01:00:00+00:00|session|stop|
'''
