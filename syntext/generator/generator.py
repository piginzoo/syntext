from syntext.utils.utils import debug_save_image
from multiprocessing import Process, Queue
from PIL import Image, ImageDraw, ImageFile
from tqdm import tqdm
import numpy as np
import os, random
import logging
import time
import math
import cv2

logger = logging.getLogger(__name__)

# 为了解决：image file is truncated (XX bytes not processed) 异常
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Generator():
    def __init__(self, config, charset, fonts, backgrounds, text_creator, augmentor):
        self.config = config
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

            # refer to : https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pil-imagefont
            w, h = font.getsize(c)
            if c == " ":  # 忽略空格，但是位置要空出来
                x_offset += w
                continue

            bbox = font.getmask(c).getbbox()
            if bbox is None:
                logger.warning("无法计算字符[%s]的bbox",c)
                x_offset += w
                continue

            ascent, descent = font.getmetrics()
            fix_height = ascent + descent  # 整个字的高度（包含上下余白，不同的字都是一个固定数）
            (width2, baseline), (offset_x, offset_y) = font.font.getsize(c)
            bbox_w = bbox[2] - bbox[0]
            bbox_h = bbox[3] - bbox[1]
            # 左右两边尽量充满
            left, right = x_offset + bbox[0], x_offset + bbox[2]
            left_padding = bbox[0]
            right_padding = w - bbox[2]
            if left_padding > right_padding:
                left = left - right_padding + 1  # 空2个像素
                right = x_offset + w - 1
            else:
                left = x_offset + 1
                right = right + left_padding - 1  # 空2个像素
            # 高度小于高1/2，补高度的1/2
            top = y_offset + bbox[1] + offset_y
            bottom = y_offset + bbox[3] + offset_y
            if (bbox_h / fix_height) < (1 / 2):
                expand = math.floor(h * 1 / 4)
                top -= expand
                bottom += expand


            char_char_bbox = [
                [left, top],
                [right, top],
                [right, bottom],
                [left, bottom]
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

        counter = 0
        error_counter = 0

        while True:

            if counter >= num: break

            image_name = "{}-{}.png".format(id, counter)
            try:
                image_path = os.path.join(dir, image_name)
                image, text, bboxes = self._create_one_image()
                image = self._pil2cv2(image)

                image, bboxes = self.augmentor.augument(image, bboxes)

                bboxes = self._revise_bboxes(bboxes)

                label_data = self.build_label_data(text, bboxes)

                if label_data is None:
                    error_counter += 1
                    continue  # 异常的话，重新生成

                cv2.imwrite(image_path, image)

                debug_save_image(image_name, image, bboxes)

                queue.put({'image': image_path, 'label': label_data})
                counter += 1
            except Exception as e:
                logger.exception("{}-{}.png 样本生成发生错误，忽略，继续....".format(id, counter))

        logger.info("[生成进程 {}] 生成完毕，退出！合计[{}]张，出现问题[{}]张".format(id, num, error_counter))

    # 坐标如果为负，则置为0
    def _revise_bboxes(self, bboxes):
        bboxes = np.array(bboxes)
        minus_indices = bboxes < 0
        bboxes[minus_indices] = 0
        return bboxes.tolist()

    def _save_label(self, queue, total_num):
        counter = 0
        pbar = tqdm(total=total_num)
        pbar_step = total_num // 100
        while True:
            try:

                if counter!=0 and counter % pbar_step ==0: pbar.update(1)

                data = queue.get()
                image = data['image']
                label = data['label']
                self.save(image, label)
                counter += 1

                if counter >= total_num:
                    logger.info("[写入进程] 完成了所有样本的写入")
                    pbar.close()
                    break
            except Exception as e:
                counter += 1
                logger.exception("[写入进程] 样本保存发生错误，忽略此错误，继续....")
        logger.info("[写入进程] 已经完成，退出")

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

        bboxes = self._caculate_position(text, font, x, y)  # 计算每个字的bbox

        return background, text, bboxes

    def execute(self, total_num, dir, worker):
        start = time.time()

        producers = []
        queue = Queue()

        consumer = Process(target=self._save_label, args=(queue, total_num))
        consumer.start()

        # 把任务平分到每个work进程中，多余的放到最后一个进程，10=>[3,3,4], 11=>[4,4,3]，原则是尽量均衡
        per_num = round(total_num / worker)
        worker_num = [0] * 10
        worker_num[0:-1] = [per_num] * (worker - 1)
        worker_num[-1] = total_num - (worker - 1) * per_num

        # 启动生成进程，并且主进程等待他们都结束才继续
        for id, num in enumerate(worker_num):
            p = Process(target=self._create_image, args=(id, queue, num, dir))
            producers.append(p)
            p.start()
        for p in producers:
            p.join()  # 要等着这些子进程结束后，主进程在往下

        logger.info("生成进程全部运行完毕，等待写入进程工作...")
        timeout = 0
        while True:
            if not consumer.is_alive(): break
            if timeout > 300:
                logger.warning("超时5分钟退出")
                consumer.terminate()
                break
            time.sleep(1)
            timeout += 1

        all_seconds = time.time() - start
        minutes = all_seconds // 60
        seconds = all_seconds % 60
        logger.info("!!! 样本生成完成，合计[%d]张，耗时: %d 分 %d 秒" % (total_num, minutes, seconds))

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
