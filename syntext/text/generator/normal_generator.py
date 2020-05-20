import time,random
from syntext.text.text_generator import TextGenerator

class DateGenerator(TextGenerator):
    def __init__(self, charset):
        super().__init__("date")
        self.charset = charset

    def generate(self):
        length = random.randint(MIN_LENGTH, MAX_LENGTH)
        s = ""
        for i in range(length):
            j = random.randint(0, len(self.charset) - 1)
            s += self.charset[j]
        # if DEBUG: print("随机生成的字符串[%s]，%d" %(s,length))
        return s