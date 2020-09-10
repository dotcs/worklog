.. _status-bars-label:

Integration into Status Bars
============================

The status can be integrated into status bars.

The integration should work with all status bars that allow to call external
programs periodically.
It has been tested with the following status bars.

- i3-status-rust_

Formatting can be customized with the ``--fmt`` flag.
The following parameters are available:

===========================  ===========
Variable                     Description
===========================  ===========
``active_tasks``             List of currently active tasks w/o statistics
``active_tasks_stats``       Similar to ``active_tasks``, but with statistics (counter)
``touched_tasks``            List of all tasks that have been touched w/o statistics
``touched_tasks_stats``      Similar to ``all_touched_tasks``, but with statistics (counter, summed time)
``break_duration``           Calculated break duration (see :ref:`auto-breaks-label`) (HH:MM:SS)
``break_duration_short``     Similar to ``break_duration``, but w/o seconds (HH:MM)
``eow``                      Calculated end of the working day (HH:MM:SS)
``eow_short``                Similar to ``eow``, but w/o seconds (HH:MM)
``overtime``                 Number of overtime hours worked on this day (HH:MM:SS)
``overtime_short``           Similar to ``overtime``, but w/o seconds (HH:MM)
``percentage_done``          Percentage of hours worked measured against the target value (w/o percent sign)
``percentage_overtime``      Percentage of overtime hours worked measured against the soft limit (w/o percent sign)
``percentage_remaining``     Percentage of hours to work until the target value is reached (w/o percent sign)
``remaining_time``           Time remaining until the end of the working day (HH:MM:SS)
``remaining_time_short``     Similar to ``remaining_time``, but w/o seconds (HH:MM)
``total_time``               Total working time (HH:MM:SS)
``total_time_short``         Similar to ``total_time``, but w/o seconds (HH:MM)
``tracking_status``          Current tracking status ('on' or 'off')
===========================  ===========

Variables must be wrapped in single curly braces:

.. code:: console

    $ wl status --fmt '{tracking_status} | {remaining_time_short} {percentage_done}%'
    on | 7:38 4%

    $ wl status --fmt '{tracking_status} | {active_tasks_stats}'
    on | (2) [task1, task2]

.. _i3-status-rust: https://github.com/greshake/i3status-rust