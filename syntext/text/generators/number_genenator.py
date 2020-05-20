from syntext.text.generator import TextGenerator
import random

class NumGenerator(TextGenerator):
    def __init__(self, config, charset):
        super().__init__("number", config)

    def generate(self,):
        # 专门用来产生数字，可能有负数，两边随机加上空格
        num = random.uniform(-self.config.MAX_GENERATE_NUM,self.config.MAX_GENERATE_NUM)
        need_format = random.choice([True,False])
        if (need_format):
            return "{:,}".format(num)
        return str(num)