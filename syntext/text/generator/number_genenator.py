from syntext.text.text_generator import TextGenerator
import random

MAX_GENERATE_NUM = 1000000000

class NumGenerator(TextGenerator):
    def __init__(self, charset):
        super().__init__("number")

    def generate(self,):
        # 专门用来产生数字，可能有负数，两边随机加上空格
        num = random.uniform(-MAX_GENERATE_NUM,MAX_GENERATE_NUM)
        need_format = random.choice([True,False])
        if (need_format):
            return "{:,}".format(num)
        return str(num)