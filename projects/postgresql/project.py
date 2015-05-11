#!/bin/python

from distgen.project import AbstractProject

class Project(AbstractProject):

    maintainer = "Pavel Raiskup <praiskup@redhat.com>"

    def inst_init(self, spec, template, sysconf):
        """
        Demonstrate logic in inst_init().
        """
        test_var = "{0}-{1}-{2}".format(sysconf['distribution'],
                                        sysconf['distversion'],
                                        sysconf['arch'])

        # Returned dict may be reused directly in yaml specification
        return {'test_var': "build_for {0}".format(str(test_var))}

    def inst_finish(self, spec, tpl, config, data):

        # We can in-place update 'data' variable generated from yaml
        # specification.
        if config['distribution'] == 'fedora':
            action = {'type': 'pkg'}
            action['action'] = "install"
            action['packages'] = ['htop']

            data['parts']['pkginstall']['data'].append(action)
