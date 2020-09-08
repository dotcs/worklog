.. _integrity-label:

Integrity check
===============

The integrity of the worklog file can be tested with the ``doctor`` commmand.
worklog will test if all start entries for both work sessions and tasks have
been closed with a corresponding stop entry.

.. code:: console

    $ wl doctor
    ERROR:worklog:Date 2020-06-17 has no stop entry.
    ERROR:worklog:Date 2020-06-18 has no stop entry.
