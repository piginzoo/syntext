from syntext.generator.generator_builder import GeneratorBuilder
from syntext.config import Config
from PIL import Image, ImageFont
import numpy as np
import argparse
import logging
import os

logger = logging.getLogger(__name__)


def __load_background(bground_dir):
    bground_list = []

    if not os.path.exists(bground_dir):
        logger.warning("样本背景图片目录不存在：%s", bground_dir)
    else:
        for img_name in os.listdir(bground_dir):
            name, ext = os.path.splitext(img_name)

            if ext.upper()!="JPG" or ext.upper()!="PNG" or ext.upper()!="JPEG": continue

            full_path = os.path.join(bground_dir, img_name)
            image = Image.open(full_path)
            if image.mode == "L":
                logger.error("图像[%s]是灰度的，转RGB", img_name)
                image = image.convert("RGB")
            bground_list.append(image)
            logger.debug("    加载背景图片：%s", full_path)
        logger.info("所有背景图片加载完毕[%d]张", len(bground_list))

    if(len(bground_list)==0):
        image = np.random.randint(200, 255, (800, 600, 3))
        bground_list.append(image)
        logger.warning("无法加载目录[%s]的背景，使用默认背景", bground_dir)

    return bground_list


# 提前生成所有字体的不同字号的字体
def __load_fonts(conf):
    font_sizes = np.arange(conf.MIN_FONT_SIZE, conf.MAX_FONT_SIZE)
    font_dir = config.RESOURCE['FONT_DIR']

    fonts = []
    for font_name in os.listdir(font_dir):
        font_name = os.path.join(font_dir, font_name)
        try:
            for size in font_sizes:
                font = ImageFont.truetype(font_name, size)
                fonts.append(font)
        except Exception as e:
            logger.warning("加载字体[%s]失败,原因：%s",font_name, str(e))
            continue
        logger.info("所有字体加载完毕[%d]个", len(fonts))

    if len(fonts)==0:
        font = ImageFont.load_default()
        logger.warning("无法加载目录[%s]的字体，使用系统默认字体", font_dir)
        fonts.append(font)
    return fonts


def __load_charset(charset_file):
    charset = open(charset_file, 'r', encoding='utf-8').readlines()
    charset = [ch.strip("\n") for ch in charset]
    charset = "".join(charset)
    charset = list(charset)
    logger.info("所有字库加载完毕[%d]个", len(charset))
    return charset


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir")
    parser.add_argument("--worker", type=int)
    parser.add_argument("--config", type=str)
    parser.add_argument("--num", type=int)
    parser.add_argument("--debug", default=False, action='store_true')
    args = parser.parse_args()

    level = logging.INFO
    if args.debug: level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d行 %(message)s"
    )

    if not os.path.exists(args.dir): os.mkdir(args.dir)

    config = Config(args.config)
    fonts = __load_fonts(config)
    backgrounds = __load_background(config.RESOURCE['BACKGROUND_DIR'])
    charset = __load_charset(config.RESOURCE['CHARSET'])

    builder = GeneratorBuilder()
    generator = builder.build(config, charset, fonts, backgrounds)

    generator.execute(total_num=args.num, dir=args.dir, worker=args.worker)
