from distgen.project import AbstractProject


class Project(AbstractProject):
    def inst_init(self, specfiles, template, sysconfig):
        self.foo = 'bar'

    def inst_finish(self, specfiles, template, sysconfig, spec):
        pass
