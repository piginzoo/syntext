from syntext.text.postprocess import PostProcessor
from syntext.utils import utils
import random

class SpecialProcessor(PostProcessor):
    def __init__(self, config):
        super().__init__("special",config)

    # 对一些特殊字符做多一些样本
    def process(self,s):
        if not self.is_accept(self.config.POSSIBILITY_SPECIAL): return s

        # logger.debug("原字符：%s",s)
        specials = "!@#$%^&*()-_+={}[]|\<>,.。;:、?/'\"《》①②③④⑤⑥⑦⑧⑨⑩【】￥"
        num = random.randint(1,self.config.MAX_SPECIAL_NUM)
        for i in range(num):
            c = random.choice(specials)
            pos = random.randint(0,len(s))
            s = s[:pos] + c + s[pos:]
        # logger.debug("插入特殊字符后：%s", s)
        return s