.. _tasks-label:

Tasks
=====

Tasks are pieces of work to be done or undertaken during a working session.
They can be used to track time for certain one-time or re-occuring work
pieces.

Each task must have a unique identifier that can be chosen freely.
If the same identifier is used twice worklog assumes that this is the same
task.
This is especially important when generating statistics and reports for
individual tasks.

The following starts and stops a new task.
It is assumed that this happens during a running
:ref:`Session<sessions-label>`.

.. code:: shell

    wl task start orga-mails    # starts tracking of a task
    wl task stop orga-mails     # stops tracking of a task

Similar to :ref:`sessions-label` the flags ``--offset-minutes`` and
``--time`` can be used to use an offset or absolute time value for the new
entry.

Because often the open tasks should be stopped when starting a new task, the
``--auto-close`` flag can be used when starting a new task.
This automatically stops all other running tasks.

.. code:: shell

    wl task start task1 --offset-minutes -10
    wl task start task2 --auto-close          # will close task1 first and then start task2

All previously used task identifiers can be listed.

.. code:: shell

    wl task list

Also for each task identifier a report can be generated which will list all
the occurencies:

::

    $ wl task report orga-mails

    Log entries:

       Date    Start     Stop    Duration
    2020-09-08 07:48:54 07:50:42 00:01:48
    2020-09-08 07:57:31 08:02:37 00:05:06
    ---
    Daily aggregated:

               Duration
    Date
    2020-09-08 00:06:54
    ---
    Total: 0 days 00:06:54