import time,random
from syntext.text.generator import TextGenerator

class DateGenerator(TextGenerator):
    def __init__(self, config, charset):
        super().__init__("normal", config)
        self.charset = charset

    def generate(self):
        length = random.randint(self.config.MIN_LENGTH, self.config.MAX_LENGTH)
        s = ""
        for i in range(length):
            j = random.randint(0, len(self.charset) - 1)
            s += self.charset[j]
        # if DEBUG: print("随机生成的字符串[%s]，%d" %(s,length))
        return s