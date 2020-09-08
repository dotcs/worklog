.. _quickstart-label:

Quickstart
==========

Installation
------------

As the compiled worklog package is hosted on the Python Package Index (PyPI)
you can easily install it with pip

.. code:: console

    $ pip install dcs-worklog

worklog is a CLI tool that registers itself as ``wl``.

Basic usage
-----------

By default worklog uses a file ``.worklog`` located in the home directory of
the user.
To start a new session use the command 

.. code:: console

    $ wl commit start

This creates a new session which is now active.
To see the status of your tracked work of the current day use the ``status``
command.
A summary of the current day will be shown.

.. code:: console

    $ wl status
    Status            : Tracking on
    Total time        : 00:05:04 (  1%)
    Remaining time    : 07:54:56 ( 99%)
    Overtime          : 00:00:00 (  0%)
    Break Duration    : 00:00:00
    All touched tasks : (0) []
    Active tasks      : (0) []

By default worklog assumes that a working day has 8 hours.
It has a soft limit of 10 hours.
Both rules can be adjusted, see section :ref:`config-files-label`.

Each CLI command has a ``--help`` flag that can be used to get information
about all possible parameters and their descriptions, e.g.

.. code:: console

    $ wl status --help           
    usage: Worklog status [-h] [--yesterday | --date DATE] [--fmt FMT]

    The status commend shows the tracking results for an individual day. By
    default the current day is selected. For integration of the current status
    into a status bar, use the `--fmt` argument.

    optional arguments:
    -h, --help   show this help message and exit
    --yesterday  Returns the status of yesterday instead of today.
    --date DATE  Date in the form YYYY-MM-DD
    --fmt FMT    Use a custom formatted string

It is possible to define a different output format for the ``status`` command
with the ``--fmt`` option.
This is especially useful when the output of worklog should be embedded into
a status bar.
See :ref:`status-bars-label` for more information on the possible options.

While ``wl commit`` starts and ends sessions it is also possible to log tasks.
Tasks are pieces of work to be done or undertaken during a working session.
The command is similar

.. code:: console

    $ wl task start my-task-id

where ``my-task-id`` is the identifier of the task that can be chosen freely.

The status of running tasks can be checked with the ``wl status`` command as
seen above.
The output covers active and touched tasks.

.. code:: console

    $ wl status
    Status            : Tracking on
    Total time        : 00:14:05 (  3%)
    Remaining time    : 07:45:55 ( 97%)
    Overtime          : 00:00:00 (  0%)
    Break Duration    : 00:00:00
    All touched tasks : (0) []
    Active tasks      : (1) [my-task-id]

The following command closes a running task

.. code:: console

    $ wl task stop my-task-id

The status command then no longer shows ``my-task-id`` as a touched task and
summarizes the time that has been spent on the task today.

.. code:: console

    $ wl status
    Status            : Tracking on
    Total time        : 00:19:09 (  4%)
    Remaining time    : 07:40:51 ( 96%)
    Overtime          : 00:00:00 (  0%)
    Break Duration    : 00:00:00
    All touched tasks : (1) [my-task-id (00:05:05)]
    Active tasks      : (0) []

Finally the work session can be stopped by using the command

.. code:: console

    $ wl commit stop

The ``status`` command then shows that the current work session has been
paused.

.. code:: console

    $ wl status
    Status            : Tracking off
    Total time        : 00:21:07 (  4%)
    Remaining time    : 07:38:53 ( 96%)
    Overtime          : 00:00:00 (  0%)
    Break Duration    : 00:00:00
    All touched tasks : (1) [my-task-id (00:05:05)]
    Active tasks      : (0) []