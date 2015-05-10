from __future__ import print_function
import six

import sys
import copy
from pathmanager import PathManager


def die(msg):
    # TODO: use logging
    print(msg)
    sys.exit(2)

def error(msg):
    # TODO: use logging
    print(msg)


def merge_yaml(origin, override):
    """
    Merge simple yaml node recursively.  If the node is non-dict, return itself,
    otherwise recurse down for each item.
    """
    if isinstance(origin, dict) and isinstance(override, dict):
        for k, v in six.iteritems(override):
            if k in origin:
                origin[k] = merge_yaml(origin[k], override[k])
            else:
                origin[k] = copy.deepcopy(override[k])
        return origin

    return copy.deepcopy(override)


def __recursive_load(pm, stack, filename):
    if filename in stack:
        die("already parsed " + filename)

    stack.append(filename)

    import yaml
    try:
        yaml_data = yaml.load(pm.open_file(
            filename,
            fail=True,
            file_desc="configuration file",
        ))
    except yaml.YAMLError, exc:
        print("Error in configuration file: {0}".format(exc))
        sys.exit(1)

    if yaml_data and "extends" in yaml_data:
        subdata = __recursive_load(pm, stack, yaml_data["extends"])
        yaml_data = merge_yaml(subdata, yaml_data)

    return yaml_data


def load_config(path, config_file, context=None):
    yaml_data = __recursive_load(PathManager(path), [], config_file)
    return yaml_data
