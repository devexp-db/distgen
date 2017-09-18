.. _rerendering:

Recursive Rendering
===================

*Note: This is an experimental feature introduced in version 0.16. It is
subject to change or removal in future versions. Use at your own risk.*

Recursive rendering is a concept similar to :ref:`macros <macros>`, perhaps
aimed at obsoleting it altogether one day. For now, both of these live side
by side.

The idea behind recursive rendering is simple:

* The template is rendered recursively until it stops changing.
* Spec values can contain references to other spec or config values.
  
Note two things:

* Maximum number of rendering passes is always limited to a reasonably
  small integer (currently passed via ``--max-passes X`` on command line)
  to make sure the re-rendering loop ends.
* Recursive rendering is currently turned off, as ``--max-passes`` is
  set to ``1``.

Example
-------

Let's consider the following spec::

    name: "myname"
    help: "This is a help for {{ config.os.id }}/{{ spec.myname }} image."

Let's try rendering a very simple template that looks like this::

    {{ spec.help }}

* In the first rendering pass, ``{{ spec.help }}`` will get substitued.
* In the second rendering pass, ``{{ config.os.id }}`` and
  ``{{ spec.myname }}`` will get substitued.
* The third rendering pass will find out that there are no changes and
  will end recursive rendering (so 3 passes are necessary).

Usage
-----

As of now, recursive rendering is turned off by default (in other words,
there's just one rendering pass). To turn it on, pass a number higher than
2 to ``dg``'s ``--max-passes`` commandline switch. For example::

    dg --distro fedora-26-x86_64.yaml --spec myspec.yaml --template Dockerfile --max-passes 10
