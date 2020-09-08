.. _logs-label:

Logs
====

The main concept of worklog is to have every log entry available in a simple
text file which is formatted as a CSV file with pipes being used as the
separator chars.

A typical file looks like this

::

    2020-09-07 21:55:33+02:00|2020-09-07 21:55:33+02:00|session|start|
    2020-09-07 22:09:36+02:00|2020-09-07 22:09:36+02:00|task|start|task1
    2020-09-07 22:14:41+02:00|2020-09-07 22:14:41+02:00|task|stop|task1
    2020-09-07 22:16:40+02:00|2020-09-07 22:16:40+02:00|session|stop|

The first column is the date at which the entry has been created.
The second column is the event date, which means the date when the event has
happened.
If ``--offset-minute`` or ``--time`` flags have been used to create an entry
the second column differs from the first column, otherwise they are the same.

The file is an append-only log, so row entries appear as the user has logged
them.
This might result in out-of-order entries if a different date has been set
for the event date.

.. warning::

    Although it is possible, we recommend users to **not** edit this file
    manually but only change it through the worklog util.

To make it easier to see the sorted logs the following command can be used:

.. code:: console

    $ wl log

which will show the last 10 records by default.
The ``--number`` flag can be used to change the number of rows that should be
printed.
To see the full log the ``--all`` flag can be used.
By default the system's pager is used if more than 10 entries are requested.
To force output to stdout the ``--no-pager`` flag can be set.

Sometimes it is useful to only show the logs for sessions or tasks.
The ``--category`` flag can be used to limit the output to either sessions or
tasks.

.. code:: console

    $ wl log --category session    # will only show sessions
    $ wl log --category task       # will only show tasks
