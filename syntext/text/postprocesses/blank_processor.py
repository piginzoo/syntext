from syntext.text.postprocess import PostProcessor
from syntext.utils import utils
import random

class BlankProcessor(PostProcessor):
    def __init__(self, config):
        super().__init__("blank",config)


    def process(self,text):
        if not self.is_accept(self.config.POSSIBILITY_BLANK): return text

        # 如果数字/日期，只在收尾加入空格
        if utils.is_number(text) or utils.is_date(text):
            return self._generate_blanks_only_head_tail(text)

        self._generate_blanks_at_random_pos(text)

    # 只在头尾加入空格
    def _generate_blanks_only_head_tail(self, chars):
        # 随机前后加上一些空格
        _blank_num1 = random.randint(1, self.config.MAX_BLANK_NUM)
        _blank_num2 = random.randint(1, self.config.MAX_BLANK_NUM)
        return (" " * _blank_num1) + chars + (" " * _blank_num2)

    # 随机在前后或者中间加入空格
    def _generate_blanks_at_random_pos(self, chars):
        # print("%s:%d" % (chars,len(chars)))
        _blank_num = random.randint(1, self.config.MAX_BLANK_NUM)
        for i in range(_blank_num):
            max_pos = len(chars)
            rand_pos = random.randint(0, max_pos)
            chars = chars[:rand_pos] + " " + chars[rand_pos:]
        # print("%s:%d" % (chars, len(chars)))
        return self._generate_blanks_only_head_tail(chars)
