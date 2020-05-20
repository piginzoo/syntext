import random

class TextGenerator():
    def __init__(self,name):
        self.name = name

    def _random_accept(accept_possibility):
        return np.random.choice([True,False], p = [accept_possibility,1 - accept_possibility])

    def generate(self):
        pass

    # 只在头尾加入空格
    def _generate_blanks_only_head_tail(self,chars):
        # 随机前后加上一些空格
        _blank_num1 = random.randint(1, MAX_BLANK_NUM)
        _blank_num2 = random.randint(1, MAX_BLANK_NUM)
        return   (" " * _blank_num1) + chars + (" " * _blank_num2)

    # 随机在前后或者中间加入空格
    def _generate_blanks_at_random_pos(self,chars):
        # print("%s:%d" % (chars,len(chars)))
        if not _random_accept(POSSIBILITY_BLANK): return chars
        _blank_num = random.randint(1,MAX_BLANK_NUM)
        for i in range(_blank_num):
            max_pos = len(chars)
            rand_pos = random.randint(0,max_pos)
            chars = chars[:rand_pos] + " " + chars[rand_pos:]
        # print("%s:%d" % (chars, len(chars)))
        return self._generate_blanks_only_head_tail(chars)