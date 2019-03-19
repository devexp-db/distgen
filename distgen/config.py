import six
import copy

from distgen.err import fatal
from distgen.pathmanager import PathManager


def _merge_yaml(origin, override):
    """
    Merge simple yaml node recursively.  If the node is non-dict, return
    itself, otherwise recurse down for each item.
    """
    if isinstance(origin, dict) and isinstance(override, dict):
        for k, v in six.iteritems(override):
            if k in origin:
                origin[k] = _merge_yaml(origin[k], override[k])
            else:
                origin[k] = copy.deepcopy(override[k])
        return origin

    return copy.deepcopy(override)


def merge_yaml(origin, override):
    old = copy.deepcopy(origin)
    new = copy.deepcopy(override)
    return _merge_yaml(old, new)


def __recursive_load(pm, stack, filename):
    if filename in stack:
        fatal("already parsed " + filename)

    stack.append(filename)

    import yaml
    try:
        yaml_data = yaml.load(
            pm.open_file(
                filename,
                fail=True,
                file_desc="configuration file",
            ),
            Loader=yaml.SafeLoader,
        )
    except yaml.YAMLError as exc:
        fatal("Error in configuration file: {0}".format(exc))

    if yaml_data and "extends" in yaml_data:
        subdata = __recursive_load(pm, stack, yaml_data["extends"])
        yaml_data = merge_yaml(subdata, yaml_data)

    return yaml_data


def load_config(path, config_file, context=None):
    pm = PathManager(path, file_suffix='.yaml')
    yaml_data = __recursive_load(pm, [], config_file)
    return yaml_data
