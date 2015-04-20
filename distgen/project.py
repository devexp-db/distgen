class AbstractProject():
    tplgen = None

    maintainer = "unknown <unknown@unknown.com>"

    """
    Initially, I was thinking about "task_root" as the main task, which could
    have dependencies (children), etc.  However, we'll see whether this is
    necessary in future.  Most probably we'll be fine with simple generator and
    we let the dependency resolution upon make or some other cool tool.
    """
    task_root = None

    def __init__(self):
        # self.ctx = ctx
        # self.config = self.ctx.system_config
        # # Just a shortcut to dirs.
        # self.dirs = ctx.system_config["dirs"]
        # self.task_root = TaskTemplate(ctx)
        pass


    def inst_init(self, spec, template):
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


    def build(self):
        self.prebuild()
        self.task_root.perform()


    def initialize(self):
        pass
