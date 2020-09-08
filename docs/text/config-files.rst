.. _config-files-label:

Configuration Files
===================

worklog comes with a default configuration file that looks like this:

.. literalinclude:: ../../worklog/config.cfg

It is possible to overwrite single or multiple configuration values by
creating a file ``~/.config/worklog/config`` which will overwrite the default
configuration values.

For the sake of an example let us assume that a personalized config file has
been created with the following content.

::

    [worklog]
    path = ~/.my-worklog-file

    [workday]
    hours_max = 12


Those configuration changes how change where the worklog file is located.
worklog now uses the file ``~/.my-worklog-file`` as its back-end.
Also the soft-limit has been increased from 10 hours to 12 hours.

Any value in the default configuration can be overwritten in this way.
For example in the section :ref:`auto-breaks-label` the configuration file
will be modified in order to configure automatic breaks.
