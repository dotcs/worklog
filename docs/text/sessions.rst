.. _sessions-label:

Sessions
========

The main task of a worklog util is to track work sessions.
A session typically begins in the morning and stops for lunch.
It continues after lunch and ends in the evening.
:ref:`auto-breaks-label` can also be configured if wished.

New sessions can be started and stopped with the ``session`` command:

.. code:: console

    $ wl session start  # starts a session
    $ wl session stop   # ends a session

In case the session should start earlier the ``--offset-minutes`` flag can
be used:

.. code:: console

    $ wl session start --offset-minutes -15  # starting time is now minus 15 minutes (in the past)
    $ wl session start --offset-minutes +15  # starting time is now plus 15 minutes (in the future)

Alternatively absolute times can also be used:

.. code:: console

    $ wl session start --time 08:15   # starting time is today at 08:15

If an entry should be created for a different day an `ISO
8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ formatted
string should be used.

.. code:: console

    $ wl session start --time 2020-01-01T08:15:00+02:00

In case no timezone information is given the local timezone is used.

To stop a session all :ref:`tasks-label` must be stopped first.
Tasks are explained in more detail in the next section.
In case this should be done automatically the ``--force`` flag can be used.

.. code:: console

    $ wl session start         # start a new session
    $ wl task start foobar    # start a task called 'foobar'

    $ wl session stop          # does not work, because tasks are still running
    Fatal. Cannot stop, because tasks are still running. Stop running tasks first: ['foobar'] or use --force flag.

    $ wl session stop --force  # does work, tasks are stopped automatically

