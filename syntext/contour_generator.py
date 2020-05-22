from syntext.generator import Generator
from syntext.text.manager import RandomTextGenerator
from syntext.augmentor import Augumentor
from syntext.utils.utils import debug


class ContourGenerator(Generator):
    """
    会对每一个字进行标注，使用四点标注法。
    """

    def __init__(self, config, charset, fonts, backgrounds, saver):

        super().__init__(config, charset, fonts, backgrounds, saver)
        self.text_creator = RandomTextGenerator(config, charset)
        self.augmentor = Augumentor(config)





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
        debug("text：[%s], char_bboxes len(%d), char_bboxes:%r", text, len(char_bboxes), char_bboxes)
        data = {}
        data['label'] = text
        data['pos'] = []
        i = 0
        for char in text:

            if char == " ": continue  # 空格不标注的

            debug("char_bboxes[i]:%r", char_bboxes[i])
            pos = {
                'word': char,
                'bbox': char_bboxes[i]
            }
            data['pos'].append(pos)
            debug("pos:%r", pos)

            i += 1

        return data
