#!/bin/python

from distgen.project import AbstractProject

class Project(AbstractProject):

    maintainer = "Pavel Raiskup <praiskup@redhat.com>"

    def inst_init(self, spec, template, sysconf):
        return {}
