from distgen.project import AbstractProject


class Project(AbstractProject):
    def inst_init(self, specfiles, template, sysconfig):
        self.somestuff = 'interesting'

    def inst_finish(self, specfiles, template, sysconfig, spec):
        pass
