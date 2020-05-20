from pkgutil import walk_packages
import importlib
import inspect
import datetime

date_formatter = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%y年%m月%d日",
            "%Y%m%d"
            "%y%m%d",
            "%y-%m-%d ",
            "%y/%m/%d ",
]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_date(s):
    for format in date_formatter:
        try:
            datetime.datetime.strptime(s,format)
            return True
        except ValueError:
            return False


def dynamic_load(module_name, parent_class):
    print(module_name)
    base_module = importlib.import_module(module_name)
    classes = []

    print(dir(base_module))
    for _, name, is_pkg in walk_packages(base_module.__path__, prefix=f"{module_name}."):
        if is_pkg: continue

        module = importlib.import_module(name)

        for name, obj in inspect.getmembers(module):

            if not inspect.isclass(obj): continue
            if not issubclass(obj,parent_class): continue
            if obj==parent_class: continue

            classes.append(obj)

    return classes