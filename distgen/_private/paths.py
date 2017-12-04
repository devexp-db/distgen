from .abstract_paths import PathsAbstract


class Paths(PathsAbstract):
    paths = {
        'templatepath': {
            'source': ['templates'],
            'install': ['share/distgen/templates'],
        },

        'distconfpath': {
            'source': ['distconf'],
            'install': ['share/distgen/distconf'],
        },
    }


paths = Paths(['distgen', '_private'])
