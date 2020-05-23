from syntext.utils.utils import debug_save_image
from multiprocessing import Process, Queue
from syntext.augmentor import Augumentor
from PIL import Image, ImageDraw
import numpy as np
import os, random
import traceback
import logging
import time
import sys
import cv2

logger = logging.getLogger(__name__)


class Generator():
    def __init__(self, config, charset, fonts, backgrounds, saver):
        self.config = config
        self.worker = config.COMMON['WORKER']
        self.charset = charset
        self.fonts = fonts
        self.backgrounds = backgrounds
        self.saver = saver
        self.augmentor = Augumentor(config)

    # 因为英文、数字、符号等ascii可见字符宽度短，所以要计算一下他的实际宽度，便于做样本的时候的宽度过宽
    def _caculate_text_shape(self, text, font):
        # 获得文件的大小,font.getsize计算的比较准
        width, height = font.getsize(text)
        return width, height

    def _caculate_position(self, text, font):
        char_bboxes = []
        offset = 0
        for c in text:
            w, h = font.getsize(c)
            if c == " ":
                offset += w
                continue
            char_char_bbox = [
                [offset, 0],
                [offset + w, 0],
                [offset + w, h],
                [offset, h]
            ]
            char_bboxes.append(char_char_bbox)
            offset += w
        return char_bboxes

    # 产生随机颜色, 各通道小于
    def _get_random_color(self):
        base_color = random.randint(0, 128)
        noise_r = random.randint(0, 100)
        noise_g = random.randint(0, 100)
        noise_b = random.randint(0, 100)
        noise = np.array([noise_r, noise_g, noise_b])
        font_color = (np.array(base_color) + noise).tolist()
        return tuple(font_color)

    def _choose_font(self):
        font_color = self._get_random_color()
        return random.choice(self.fonts), font_color

    # 生成一张图片
    def _choose_backgournd(self, width, height):
        bground = random.choice(self.backgrounds)
        x = random.randint(0, bground.size[0] - width)
        y = random.randint(0, bground.size[1] - height)
        retry = 0
        while x < 0 or y < 0:
            print("[ERROR] 这张图太小了，换一张")
            bground = random.choice(self.backgrounds)
            x = random.randint(0, bground.size[0] - width)
            y = random.randint(0, bground.size[1] - height)
            retry += 1
            if retry >= 5:
                print("[ERROR] 尝试5次，无法找到合适的背景，放弃")
                return None

        bground = bground.crop((x, y, x + width, y + height))
        return bground

    def charset(self):
        pass

    def save_image(self, image, path):
        cv2.imwrite(path, image)

    def _create_image(self, id, queue, num, dir):

        for i in range(num):
            try:
                image_name = f"{id}-{i}.png"
                image_path = os.path.join(dir, image_name)
                image, text, bboxes = self.create_image()
                image = self._pil2cv2(image)
                image, bboxes = self.augmentor.augument(image, bboxes)
                label_data = self.build_label_data(text, bboxes)
                self.save_image(image, image_path)
                debug_save_image(image_name, image, label_data)
                queue.put({'image': image_path, 'label': label_data})
            except Exception as e:
                traceback.print_exc()
                logger.error("[#%d-%d]样本生成发生错误，忽略此错误[%s]，继续...." % (id, i, str(e)))

        logger.info("生成进程[%d]生成完毕，合计[%d]张" % (id, num))

    def _save_label(self, queue, total_num):
        counter = 0
        while True:
            try:
                data = queue.get()
                image = data['image']
                label = data['label']

                self.saver.save(image, label)
                counter += 1

                if counter >= total_num:
                    logger.info("完成了所有的样本生成")
                    break
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error("样本保存发生错误，忽略此错误，继续....", str(e))

    # 子类可能会重载
    def build_label_data(self, text, char_bboxes):
        return text

    def _pil2cv2(self, image):
        # PIL图像转成cv2
        image = image.convert('RGB')
        image = np.array(image)
        image = image[:, :, ::-1]
        return image

    def create_image(self):

        text = self.text_creator.generate()
        font, color = self._choose_font()
        bboxes = self._caculate_position(text, font)
        width, height = self._caculate_text_shape(text, font)
        background = self._choose_backgournd(width, height)

        image = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, fill=color, font=font)
        background.paste(image, (0, 0), image)

        return background, text, bboxes

    def save_label(self, label_data):
        raise NotImplementedError("需要子类化")

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
            if timeout > 30:
                logger.warning("超时30秒退出")
                consumer.terminate()
                break

            time.sleep(1)
            timeout += 1
            print(".", end='')
            sys.stdout.flush()

        logger.info("!!! 样本生成完成，合计[%d]张" % total_num)
