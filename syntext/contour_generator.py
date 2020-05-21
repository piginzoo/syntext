from syntext.generator import Generator
from syntext.text.manager import RandomTextGenerator
from syntext.augment.augmentor import Augumentor
from PIL import Image, ImageDraw


class ContourGenerator(Generator):
    """
    会对每一个字进行标注，使用四点标注法。
    """

    def __init__(self, config, charset, fonts, backgrounds, saver):

        super().__init__(config, charset, fonts, backgrounds, saver)
        self.text_creator = RandomTextGenerator(config, charset)
        self.augmentor = Augumentor(config)

    # 计算每个非空格字符的位置(每个字符使用4点坐标标记位置)
    def caculate_position(self, text, font):
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

    def create_image(self):

        text = self.text_creator.generate()
        font, color = self.choose_font()
        char_bboxes = self.caculate_position(text, font)

        width, height = self._caculate_text_shape(text, font)
        background = self.choose_backgournd(width, height)

        image = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, fill=color, font=font)

        image, char_bboxes = self.augmentor.augument(image, char_bboxes)

        background.paste(image, (0, 0), image)

        label_data = self.build_label_data(text, char_bboxes)

        return image, label_data

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
    def build_label_data(self, text, char_bboxes):
        data = {}
        data['label'] = text
        data['pos'] = []
        for i,char in enumerate(text):
            if char == " ": continue # 空格不标注的
            # print(char_bboxes[i])
            pos = {
                'word': char,
                'bbox': char_bboxes[i]
            }
            data['pos'].append(pos)

        return data
