from PIL import Image, ImageFont
from syntext.utils.utils import debug_save_image
from multiprocessing import Process, Queue
from PIL import Image, ImageDraw, ImageFile
import numpy as np
import os, random
import traceback
import logging
import time
import math
import sys
import cv2


# https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pil-imagefont

def draw_bbox(c, font, x_offset, y_offset):
    width, height = font.getsize(c)
    bbox = font.getmask(c).getbbox()
    ascent, descent = font.getmetrics()
    fix_height = ascent + descent  # 整个字的高度（包含上下余白，不同的字都是一个固定数）
    (width2, baseline), (offset_x, offset_y) = font.font.getsize(c)
    bbox_w = bbox[2] - bbox[0]
    bbox_h = bbox[3] - bbox[1]
    print("(width,height):", (width, height))
    print("(ascent,descent):", (ascent, descent))
    print("(width, baseline):", (width2, baseline))
    print("(offset_x,offset_y):", (offset_x, offset_y))
    print("ascent-offset_y:", ascent - offset_y)
    print("bbox:", bbox)
    print("fix_height:", fix_height)
    print("(bbox_w,bbox_h):", (bbox_w, bbox_h))
    print("-----------")

    """
    -----------
    (width,height): (25, 43)
    (ascent,descent): (43, 8)
    (width, baseline): (25, 42)
    (offset_x,offset_y): (0, 1)
    ascent-offset_y: 42
    bbox: (2, 0, 23, 9)
    fix_height: 51
    (bbox_w,bbox_h): (21, 9)
    -----------
    """

    import random, math
    color = random.choice(["red", "green", "blue", "yellow"])

    # 左右两边尽量充满
    left, right = x_offset + bbox[0], x_offset + bbox[2]
    left_padding = bbox[0]
    right_padding = width - bbox[2]
    if left_padding > right_padding:
        left = left - right_padding + 1  # 空2个像素
        right = x_offset + width - 1
        print("左面补%d个点" % right_padding)
    else:
        left = x_offset + 1
        right = right + left_padding - 1  # 空2个像素
        print("右面补%d个点" % left_padding)

    # 高度小于高1/2，补高度的1/2
    top = y_offset + bbox[1] + offset_y
    bottom = y_offset + bbox[3] + offset_y
    if (bbox_h / fix_height) < (1 / 2):
        expand = math.floor(height * 1/4)
        print("上下补点:%d个像素" % expand)
        top -= expand
        bottom += expand

    draw.rectangle(
        (
            (left, top),
            (right, bottom)
        ),
        outline=color)
    draw.rectangle(
        (
            (x_offset, y_offset),
            (x_offset + width, y_offset + OFFSET)
        ),
        outline="black")
    return x_offset + width


text = "我爱北京天安门0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()-_+=×{}[]|\<>,.。;:、?/“”‘’°￥《》①②③④⑤⑥⑦⑧⑨⑩【】○●□■~"

OFFSET = 50

font = ImageFont.truetype('data/fonts/simsun.ttc', 50)
width, height = font.getsize(text)
image = Image.new('RGBA', (width + 2 * OFFSET, height + 2 * OFFSET))
draw = ImageDraw.Draw(image)
draw.text((OFFSET, OFFSET), text, fill=(0, 0, 0), font=font)

offset = OFFSET
for c in text:
    offset = draw_bbox(c, font, offset, OFFSET)

image.save("data/debug/font.png")

# run it: python -m syntext.test.test_font_size  && open data/debug/font.png
