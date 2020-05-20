def _dynamic_load_generators(is_valid=lambda entity: True):
    MODULE_PATH = "syntext/text/generator"
    modules = []
    from pkgutil import walk_packages
    for _, name, is_pkg in walk_packages(MODULE_PATH):
        if is_pkg:continue
        module_code = __import__(name)
        contents = dir(module_code)
        for thing in contents:
            if is_valid(thing):
                modules.append(thing)
    return modules