from pkgutil import walk_packages
import numpy as np
import importlib
import inspect
import datetime
import logging
import cv2
import os


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



def debug_save_image(name, image, bboxes): # bboxes[N,M,2]
    if not DEBUG: return

    image = image.copy()
    debug_dir = "data/debug/bbox_images"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    debug_image_path = os.path.join(debug_dir, name)

    for one_word_bboxes in bboxes:
        # print(one_word_bboxes)
        one_word_bboxes = np.array(one_word_bboxes)
        cv2.polylines(image, [one_word_bboxes], isClosed=True, color=(0, 0, 255))

    cv2.imwrite(debug_image_path,image)


def dynamic_load(module_name, parent_class):
    base_module = importlib.import_module(module_name)
    classes = []

    for _, name, is_pkg in walk_packages(base_module.__path__, prefix="{}.".format(module_name)):
        if is_pkg: continue

        module = importlib.import_module(name)

        for name, obj in inspect.getmembers(module):

            if not inspect.isclass(obj): continue
            if not issubclass(obj, parent_class): continue
            if obj == parent_class: continue

            classes.append(obj)

    return classes
