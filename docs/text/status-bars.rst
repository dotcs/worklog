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
break_duration       tbd
end_of_work          tbd
overtime             tbd
overtime_short       tbd
percentage           tbd
percentage_overtime  tbd
percentage_remaining tbd
remaining_time       tbd
remaining_time_short tbd
total_time           tbd
==================== ===========

Variables must be wrapped in single curly braces, such as

::

    wl status --fmt '{status} | {remaining_time_short} {percentage}%'

The output of the command above looks like this

::

    off | 7:38 4%

.. _i3-status-rust: https://github.com/greshake/i3status-rust