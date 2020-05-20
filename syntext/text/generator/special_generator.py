import time,random
from syntext.text.text_generator import TextGenerator

class DateGenerator(TextGenerator):
    def __init__(self):
        super().__init__("date")

    def generate(self):
        if not _random_accept(POSSIBILITY_SPECIAL): return s

        # logger.debug("原字符：%s",s)
        specials = "|,.。-+/＊()"
        num = random.randint(1, MAX_SPECIAL_NUM)
        for i in range(num):
            c = random.choice(specials)
            pos = random.randint(0, len(s))
            s = s[:pos] + c + s[pos:]
        # logger.debug("插入特殊字符后：%s", s)
        return s
