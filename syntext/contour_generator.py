from syntext.generator import Generator
from syntext.saver.saver import ContourSaver
from syntext.text.manager import RandomTextGenerator
from syntext.augment.augmentor import Augumentor
from PIL import Image, ImageDraw
import random


"""
会对每一个字进行标注，使用四点标注法。
"""
class ContourGenerator(Generator):

    def __init__(self, config, charset, fonts, backgrounds,saver):

        super().__init__(config, charset, fonts, backgrounds)
        self.text_creator = RandomTextGenerator(config, charset)
        self.augmentor = Augumentor(config)

    # 计算每个非空格字符的位置(每个字符使用4点坐标标记位置)
    def caculate_position(self,text,font):
        pos = []
        offset = 0
        for c in text:
            w, h = font.getsize(c)
            if c == " ":
                offset += w
                continue
            char_pos = [
                [offset,0],
                [offset+w,0],
                [offset+w,h],
                [offset,h]
            ]
            pos.append(char_pos)
            offset += w
        return pos

    def create_image(self):

        text = self.text_creator.generate()
        font,color = self.choose_font()
        pos = self.caculate_position(text,font)

        width, height = self._caculate_text_shape(text,font)
        background = self.choose_backgournd(width, height)

        image = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, fill=color, font=font)

        image, label_data = self.augmentor.augument(image,pos)

        background.paste(image, (0, 0), image)

        return image, label_data

