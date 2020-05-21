from pkgutil import walk_packages
import importlib
import inspect
import datetime
import logging

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
            datetime.datetime.strptime(s, format)
            return True
        except ValueError:
            return False


DEBUG = True


def debug(*args):
    if not DEBUG: return
    logging.debug(*args)


import os
import numpy as np
from PIL import ImageDraw

def debug_save_image(name, image, label):
    if not DEBUG: return

    image = image.copy()
    debug_dir = "data/debug/bbox_images"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    debug_image_path = os.path.join(debug_dir, name)

    draw = ImageDraw.Draw(image)

    # {
    #   "label":"你好世界！",
    #   "pos":[
    #       {
    #           "bbox": [[x1,y1],[x1,y1],[x1,y1],[x1,y1]],
    #           "word": "你"
    #       },
    #       ....
    #   ]
    # }
    if type(label)==dict and "pos" in label:
        for pos in label['pos']:
            bboxes = pos['bbox']
            bboxes = [(x[0],x[1]) for x in bboxes ]
            draw.polygon(bboxes,outline="red")
        image.save(debug_image_path)


def dynamic_load(module_name, parent_class):
    base_module = importlib.import_module(module_name)
    classes = []

    for _, name, is_pkg in walk_packages(base_module.__path__, prefix=f"{module_name}."):
        if is_pkg: continue

        module = importlib.import_module(name)

        for name, obj in inspect.getmembers(module):

            if not inspect.isclass(obj): continue
            if not issubclass(obj, parent_class): continue
            if obj == parent_class: continue

            classes.append(obj)

    return classes
