.. _auto-breaks-label:

Automatic Break Handling
========================

worklog can handle breaks automatically if the assumption holds true that the
duration of the break only depends on the total working time.

To configure automatic break handling please see how a custom configuration
file can be created.
This is explained in the section :ref:`config-files-label`.

To configure automatic break handling the custom configuration must overwrite
the following values:

::

    [workday]
    # Define the lower limits of minutes to work until the corresponding break is
    # automatically applied.
    auto_break_limit_minutes = [0,360,540]
    # Defines the break durations in minutes for the interval boundaries above.
    auto_break_duration_minutes = [0,30,45]

Those changes would comply with the work time rules of Germany as stated in §
4 Ruhepausen, Arbeitszeitgesetz (ArbZG).

    Die Arbeit ist durch im voraus feststehende Ruhepausen von mindestens 30
    Minuten bei einer Arbeitszeit von mehr als sechs bis zu neun Stunden und
    45 Minuten bei einer Arbeitszeit von mehr als neun Stunden insgesamt zu
    unterbrechen. Die Ruhepausen nach Satz 1 können in Zeitabschnitte von
    jeweils mindestens 15 Minuten aufgeteilt werden. Länger als sechs Stunden
    hintereinander dürfen Arbeitnehmer nicht ohne Ruhepause beschäftigt
    werden.

    -- https://www.gesetze-im-internet.de/arbzg/BJNR117100994.html


The values can be read as such:

- If all work sessions on a single day are between 0 and up to 360 minutes (=
  6 hours), then 0 minutes of pause are automatically subtracted from the
  total working time.
- If between 360 (= 6 hours) and 540 minutes (= 9 hours) are on the clock
  then 30 minutes are subtracted automatically.
- For more than 540 minutes (= 9 hours) 45 minutes are subtracted
  automatically.

.. note::

    Both lists, ``auto_break_limit_minutes`` and
    ``auto_break_duration_minutes`` must have the same shape.
    Also automatic break handling only becomes active if the length differs
    from length zero.

If automatic break handling is active then various parts of worklog will take
care of the automatic breaks.
This includes the ``status`` command and generated :ref:`reports-label`.

.. code:: console

    $ wl status --date 2020-01-01
    Status            : Tracking off
    Total time        : 08:13:07 ( 97%)
    Remaining time    : 00:16:53 (  3%)
    Overtime          : 00:00:00 (  0%)
    Break Duration    : 00:30:00
    All touched tasks : (9) [task1 (00:30:14), task2 (01:01:17), task3 (00:17:40), task4 (00:43:24), task5 (01:31:12), task6 (00:55:19), task7 (00:35:40), task8 (00:08:59), task9 (00:38:54)]
    Active tasks      : (0) []

    $ wl report --date-from 2020-W32 --date-to 2020-W33
    Aggregated by month:
    --------------------
                    Date           Total time                Break        Bookable time
                 2020-08             31:04:59             02:00:00             29:04:59
    
    Aggregated by week:
    -------------------
                    Date           Total time                Break        Bookable time
              2020-08-16             31:04:59             02:00:00             29:04:59
    
    Aggregated by day:
    ------------------
                    Date           Total time                Break        Bookable time
              2020-08-10             07:48:09             00:30:00             07:18:09
              2020-08-11             07:52:13             00:30:00             07:22:13
              2020-08-12             07:11:30             00:30:00             06:41:30
              2020-08-13             08:13:07             00:30:00             07:43:07
    
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