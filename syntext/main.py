from syntext.contour_generator import ContourGenerator
from syntext.saver.saver import ContourSaver
from PIL import Image, ImageFont
from syntext.config import Config
import numpy as np
import logging
import argparse
import os


logger = logging.getLogger(__name__)

def __load_background(bground_dir):
    bground_list = []

    for img_name in os.listdir(bground_dir):
        full_path = os.path.join(bground_dir,img_name)
        image = Image.open(full_path)
        if image.mode == "L":
            logger.error("图像[%s]是灰度的，转RGB", img_name)
            image = image.convert("RGB")
        bground_list.append(image)
        logger.debug("    加载背景图片：%s", full_path)
    logger.debug("所有图片加载完毕")

    return bground_list

# 提前生成所有字体的不同字号的字体
def __load_fonts(conf):

    font_sizes = np.arange(conf.MIN_FONT_SIZE,conf.MAX_FONT_SIZE)
    font_dir = config.RESOURCE['FONT_DIR']

    fonts = []
    for font_name in os.listdir(font_dir):
        font_name = os.path.join(font_dir,font_name)
        for size in font_sizes:
            font = ImageFont.truetype(font_name, size)
            fonts.append(font)
    return fonts

def __load_charset(charset_file):
    charset = open(charset_file, 'r', encoding='utf-8').readlines()
    charset = [ch.strip("\n") for ch in charset]
    charset = "".join(charset)
    charset = list(charset)
    if charset[-1]!=" ":
        charset.append(" ")
    return charset

def build_generator(config, charset, fonts, backgrounds):
    if config.COMMON['SAVER']:
        saver = ContourSaver(config)

    if config.COMMON['TEXT_GENERATOR']:
        text_generator = ContourGenerator(config, charset, fonts, backgrounds,saver)

    return text_generator

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir")
    parser.add_argument("--num", type=int)
    args = parser.parse_args()

    if not os.path.exists(args.dir): os.mkdir(args.dir)

    config = Config()
    fonts = __load_fonts(config)
    backgrounds = __load_background(config.RESOURCE['BACKGROUND_DIR'])
    charset = __load_charset(config.RESOURCE['CHARSET'])

    generator = build_generator(config, charset, fonts, backgrounds)

    generator.execute(total_num=args.num)