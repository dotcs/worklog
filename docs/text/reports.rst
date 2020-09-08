.. _reports-label:

Reports
=======

worklog is able to create reports that contain all session and task items in
a certain time window.

All reports contain aggregations by month, week and day.
They also contain aggregations by tasks with the total time spent on those
tasks.

The time window can be adjusted with the ``--date-from`` and ``--date-to``
arguments.
``--date-from`` is inclusive, ``--date-to`` is an exclusive time value.
By default the start of the current calendar month is selected.
Allowed input formats are YYYY-MM-DD, YYYY-MM and YYYY-WXX, with XX referring
to the week number, e.g. 35.

.. code:: console

    $ wl report --date-from 2020-W32 --date-to 2020-W33

    Aggregated by month:
    --------------------
                    Date           Total time
                 2020-08             31:04:59
    
    Aggregated by week:
    -------------------
                    Date           Total time
              2020-08-16             31:04:59
    
    Aggregated by day:
    ------------------
                    Date           Total time
              2020-08-10             07:48:09
              2020-08-11             07:52:13
              2020-08-12             07:11:30
              2020-08-13             08:13:07
    
    Aggregated by tasks:
    --------------------
               Task name           Total time
               TASK-1000             00:30:14
               TASK-1001             00:18:18
               TASK-1002             00:27:36
               TASK-1003             02:52:28
                 TKKA-10             00:46:46
                 TKKA-11             01:34:15
                 TKKA-12             02:54:41
                 TKKA-13             00:17:43
                 TKKA-14             00:30:36
                 TKKA-15             00:43:47
                 TKKA-16             00:20:09
                  orga-0             01:06:31
                  orga-1             08:16:56
                  orga-2             00:43:24
                  orga-3             01:31:12
                  orga-4             00:18:08
             orga-topic1             03:47:04
             orga-topic2             00:35:40
             orga-topic3             01:56:37
             orga-topic4             00:08:59
             orga-topic5             03:01:00
             orga-topic6             02:23:54