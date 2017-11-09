.. _spec_expansion:

Spec Expansion
==============

*Note: This feature has been experimental since version 0.16 (and called
"Recursive Rendering"). It has been changed in 0.20 and declared stable
since that version.*

Spec expansion is a concept similar to :ref:`macros <macros>`, perhaps
aimed at obsoleting it altogether one day. For now, both of these live side
by side.

The idea behind spec expansion is simple:

* Spec values can contain references to other spec or config values.
* A mechanism that runs right before template is rendered traverses
  the spec and expands and re-expands these values.
* The spec is expanded in a loop that ends when either:

  * No value has changed in last iteration.
  * Maximum allowed amount of iterations has been reached. This can be
    changed by passing ``--max-passes X`` on commandline. See :ref:`usage`
    for more information.

* Note that for yaml mappings (e.g. ``key: value``) references in ``key``
  are not expanded, only those in ``value`` are.

Example
-------

Let's consider the following spec::

    name: "myname"
    help: "This is a help for {{ config.os.id }}/{{ spec.myname }} image."

Let's try rendering a very simple template that looks like this::

    {{ spec.help }}

* In the first expansion pass of spec, ``{{ config.os.id }}`` and
  ``{{ spec.myname }}`` in ``help`` value will get substitued.
* The second expansion pass will find out that there are no changes and
  will end spec expansion (so 2 passes are necessary).
