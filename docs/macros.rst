.. _macros:

Macros
======

Macros are distgen's way to provide values that need to be expanded and
reexpanded. In other words, the yaml configuration files have no means
of value interpolation. This is why the macros system exists.

Macros can be created using any macros from the passed :ref:`config <configs>`.
They can also be passed from commandline via ``--macro "name value"`` or
loaded from a custom project file (TODO: custom project file needs
to be documented).

Several macro examples:

* ``foo $bindir/executable`` - define macro ``foo`` to expand using ``bindir``
  macro provided in passed config (usually this will expand to
  ``/usr/bin/executable``)
* ``bar $foo.sh`` - define macro ``bar`` to expand using previously defined
  ``foo`` macro (hence getting ``/usr/bin/executable.sh``)

The examples above will be available as ``macros.foo`` and ``macros.bar``
in the template.
