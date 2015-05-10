class AbstractProject():
    tplgen = None

    maintainer = "unknown <unknown@unknown.com>"


    def inst_init(self, spec, template, sysconfig):
        """
        Returns dict with data to be used in specification file.
        """
        return {}


    def inst_finish(self, spec, template, data):
        """ edit data (parsed specification) """
        pass


    def prebuild(self):
        """
        This be defined in inheritting Project
        """
        pass


    def initialize(self):
        pass
