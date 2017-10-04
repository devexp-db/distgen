class AbstractProject():
    tplgen = None

    name = "unknown-project"

    maintainer = "unknown <unknown@unknown.com>"

    def inst_init(self, specfiles, template, sysconfig):
        """
        Executed before the project.py/spec files/template is loaded and
        before all the dynamic stuff and specification is calculated.
        Now is still time to dynamically change the list of specfiles or
        adjust the system configuration. You can define a variable as an
        attribute of this project:

          self.variable = "42"

        which can be later utilized in a template like this:

          {{ project.variable }}
        """
        pass

    def inst_finish(self, specfiles, template, sysconfig, spec):
        """
        Executed after the project.py/spec files/template is loaded, and
        the specification (spec) calculated (== instantiated).  This is
        the last chance to dynamically change sysconfig or spec.
        """
        pass

    def __init__(self):
        """ Never overwrite constructor please! """
        pass

    def abstract_initialize(self):
        """
        Never overwrite this function, please.  Its currently just a
        placeholder called right after Project was instantiated and the
        right paths to templates/specs was set.
        """
        pass

    def abstract_setup_vars(self, config):
        """
        Never overwrite this function, please.
        """
        # Be careful here with changes.  Any change will survive to the next
        # call of render() method (its effect won't disappear for next
        # template).
        pass
