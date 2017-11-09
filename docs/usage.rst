.. _usage:

Commandline Usage
=================

To display distgen help, you can always run ``dg -h`` or ``dg --help``.
A detailed explanation of commandline arguments follows:

- ``--projectdir PROJECTDIR`` - path to directory with project
  (defaults to current working directory)
- ``--distro DIST`` - use distribution metadata specified by ``DIST`` yaml file
- ``--multispec MULTISPEC`` - use MULTISPEC yaml file to fill the ``TEMPLATE``
  file
- ``--multispec-selector MULTISPEC_SELECTOR`` - selectors for the multispec
  file

  - a selector must be present for each multispec group except ``distroinfo``
  - selectors must be used in form of ``<group>=<selector-name>``

- ``--spec SPEC`` - use ``SPEC`` yaml file to fill the ``TEMPLATE``
- ``--output OUTPUT`` - write result to ``OUTPUT`` file instead of stdout;
  note, that permissions of the created file respect current ``umask`` value
- ``--macros-from PROJECTDIR`` - load variables from ``PROJECTDIR``
- ``--container CONTAINER_TYPE`` - container type, e.g. ``docker``
- ``--macro MACRO`` - define distgen's macro
- ``--max-passes PASSES`` - maximum number of spec expansion passes,
  defaults to 32
- ``--template TEMPLATE`` - use ``TEMPLATE`` file, e.g. ``docker.tpl`` or
  a template string, e.g. ``{{ config.docker.from }}``
- ``--multispec-combinations`` print available multispec combinations

Note that ``--template`` and ``--multispec-combinations`` options are
mutually exclusive; exactly one of them must be used on every invocation.
