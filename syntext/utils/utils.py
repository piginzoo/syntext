from pkgutil import walk_packages
import importlib
import inspect

def dynamic_load(module_name, parent_class):
    base_module = importlib.import_module(module_name)
    classes = []

    for _, name, is_pkg in walk_packages(base_module.__path__, prefix=f"{module_name}."):
        if is_pkg: continue

        module = importlib.import_module(name)

        for name, obj in inspect.getmembers(module):

            if not inspect.isclass(obj): continue
            if not issubclass(obj,parent_class): continue
            if obj==parent_class: continue

            classes.append(obj)

    return classes