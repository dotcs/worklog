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

==================== ===========
Variable             Description
==================== ===========
active_tasks         List of currently active tasks
all_touched_tasks    List of all tasks that have been touched
break_duration       Calculated break duration (see :ref:`auto-breaks-label`)
end_of_work          Calculated end of the working day
overtime             Number of overtime hours worked on this day
overtime_short       Short version of overtime (w/o seconds)
percentage           Percentage of hours worked measured against the target value
percentage_overtime  Percentage of overtime hours worked measured against the soft limit (w/o percent sign)
percentage_remaining Percentage of hours to work until the target value is reached (w/o percent sign)
remaining_time       Time remaining until the end of the working day
remaining_time_short Time remaining until the end of the working day (w/o seconds)
status               Current tracking status ('on' or 'off')
total_time           Total working time
==================== ===========

Variables must be wrapped in single curly braces:

.. code:: console

    $ wl status --fmt '{status} | {remaining_time_short} {percentage}%'
    on | 7:38 4%

    $ wl status --fmt '{status} | {active_tasks}'
    on | (1) [task1, task2]

.. _i3-status-rust: https://github.com/greshake/i3status-rust