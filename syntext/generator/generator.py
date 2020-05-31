from syntext.utils.utils import debug_save_image
from multiprocessing import Process, Queue
from PIL import Image, ImageDraw, ImageFile
import numpy as np
import os, random
import traceback
import logging
import time
import sys
import cv2

logger = logging.getLogger(__name__)

# 为了解决：image file is truncated (XX bytes not processed) 异常
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Generator():
    def __init__(self, config, charset, fonts, backgrounds, text_creator, augmentor):
        self.config = config
        self.worker = config.COMMON['WORKER']
        self.charset = charset
        self.fonts = fonts
        self.backgrounds = backgrounds
        self.text_creator = text_creator
        self.augmentor = augmentor

    # 因为英文、数字、符号等ascii可见字符宽度短，所以要计算一下他的实际宽度，便于做样本的时候的宽度过宽
    def _caculate_text_shape(self, text, font):
        # 获得文件的大小,font.getsize计算的比较准
        width, height = font.getsize(text)

        return width, height

    def _caculate_position(self, text, font, x_offset, y_offset):
        char_bboxes = []
        for c in text:
            w, h = font.getsize(c)
            # refer to : https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pil-imagefont
            ascent, descent = font.getmetrics()
            (width, baseline), (offset_x, offset_y) = font.font.getsize(c)
            # print("y_offset",y_offset)
            # print("offset_y",offset_y)

            if c == " ": # 忽略空格，但是位置要空出来
                x_offset += w
                continue
            char_char_bbox = [
                [x_offset, y_offset+offset_y],
                [x_offset + w, y_offset+offset_y],
                [x_offset + w, h + y_offset],
                [x_offset, h + y_offset]
            ]
            char_bboxes.append(char_char_bbox)
            x_offset += w
        return char_bboxes

    # 产生随机颜色
    def _get_random_color(self):
        base_color = random.randint(0, self.config.MAX_FONT_COLOR)
        noise_r = random.randint(0, self.config.FONT_COLOR_NOISE)
        noise_g = random.randint(0, self.config.FONT_COLOR_NOISE)
        noise_b = random.randint(0, self.config.FONT_COLOR_NOISE)
        noise = np.array([noise_r, noise_g, noise_b])
        font_color = (np.array(base_color) + noise).tolist()
        return tuple(font_color)

    def _choose_font(self):
        font_color = self._get_random_color()
        return random.choice(self.fonts), font_color

    # 从大背景图中，随机切出一个和字体大小相仿的一块，宽高加入一些随机扰动
    def _choose_backgournd(self, width, height):
        # 宽高加入一些随机扰动
        width = width + random.randint(0, self.config.TEXT_WIDTH_PAD)
        height = height + random.randint(0, self.config.TEXT_HEIGHT_PAD)

        bground = random.choice(self.backgrounds)
        x = random.randint(0, bground.size[0] - width)
        y = random.randint(0, bground.size[1] - height)
        retry = 0
        while x < 0 or y < 0:
            logger.warning("背景图太小了，换一张")
            bground = random.choice(self.backgrounds)
            x = random.randint(0, bground.size[0] - width)
            y = random.randint(0, bground.size[1] - height)
            retry += 1
            if retry >= 3:
                logger.warning("尝试3次，无法找到合适的背景，放弃")
                return None

        bground = bground.crop((x, y, x + width, y + height))
        return bground

    def _create_image(self, id, queue, num, dir):

        for i in range(num):
            try:
                image_name = f"{id}-{i}.png"
                image_path = os.path.join(dir, image_name)
                image, text, bboxes = self._create_one_image()
                image = self._pil2cv2(image)


                image, bboxes = self.augmentor.augument(image, bboxes)

                bboxes = self._revise_bboxes(bboxes)

                label_data = self.build_label_data(text, bboxes)
                cv2.imwrite(image_path, image)

                debug_save_image(image_name, image, bboxes)

                queue.put({'image': image_path, 'label': label_data})
            except Exception as e:
                traceback.print_exc()
                logger.error("[#%d-%d]样本生成发生错误，忽略此错误[%s]，继续...." % (id, i, str(e)))

        logger.info("生成进程[%d]生成完毕，合计[%d]张" % (id, num))

    # 坐标如果为负，则置为0
    def _revise_bboxes(self, bboxes):
        bboxes = np.array(bboxes)
        minus_indices = bboxes < 0
        bboxes[minus_indices] = 0
        return bboxes.tolist()

    def _save_label(self, queue, total_num):
        counter = 0
        while True:
            try:
                data = queue.get()
                image = data['image']
                label = data['label']
                self.save(image, label)
                counter += 1

                if counter >= total_num:
                    logger.info("完成了所有的样本生成")
                    break
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error("样本保存发生错误，忽略此错误，继续....", str(e))

    def _pil2cv2(self, image):
        # PIL图像转成cv2
        image = image.convert('RGB')
        image = np.array(image)
        image = image[:, :, ::-1]
        return image

    def _create_one_image(self):

        text = self.text_creator.generate()
        font, color = self._choose_font()

        width, height = self._caculate_text_shape(text, font)
        image = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, fill=color, font=font)

        # 把文字，贴到背景上，背景会稍微比文字区域大一些
        background = self._choose_backgournd(width, height)
        bg_width, bg_height = background.size
        x = random.randint(0, (bg_width - width))
        y = random.randint(0, (bg_height - height))
        logger.debug("贴文字到背景的位置：(%d,%d)", x, y)
        background.paste(image, (x, y), image)

        bboxes = self._caculate_position(text, font, x, y) # 计算每个字的bbox

        return background, text, bboxes

    def execute(self, total_num, dir):
        producers = []
        queue = Queue()

        consumer = Process(target=self._save_label, args=(queue, total_num))
        consumer.start()

        num = total_num // self.worker
        for id in range(self.worker):
            p = Process(target=self._create_image, args=(id, queue, num, dir))
            producers.append(p)
            p.start()
            p.join()

        logger.info("生成进程全部运行完毕，等待写入进程工作...")
        timeout = 0
        while True:
            if not consumer.is_alive(): break
            if timeout > 3:
                logger.warning("超时30秒退出")
                consumer.terminate()
                break

            time.sleep(1)
            timeout += 1
            print(".", end='')
            sys.stdout.flush()

        logger.info("!!! 样本生成完成，合计[%d]张" % total_num)

    def save(self, image_path, label):
        lines = self.parse_lines(image_path, label)
        label_file_name, mode = self.get_label_name_and_mode(image_path)

        label_file = open(label_file_name, mode, encoding='utf-8')

        for line in lines:
            label_file.write(line)
            label_file.write("\n")
        label_file.close()

    # 子类可能会重载
    def build_label_data(self, text, char_bboxes):
        raise NotImplementedError("子类实现")

    def parse_lines(self, image_path, label):
        raise NotImplementedError("子类实现")

    def get_label_name_and_mode(self, image_path):
        raise NotImplementedError("子类实现")