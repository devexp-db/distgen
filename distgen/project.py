class AbstractProject():
    tplgen = None

    name = "unknown-project"

    maintainer = "unknown <unknown@unknown.com>"


    def inst_init(self, spec, template, config):
        """
        Returns dict with data to be used in specification file.
        """
        return {}


    def inst_finish(self, spec, template, config, data):
        """ edit data (parsed specification) """
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
