from syntext.text.generator import TextGenerator
import numpy as np
import random

class DateGenerator(TextGenerator):
    def __init__(self, config, charset):
        super().__init__("english",config)
        self.charset = charset

    def generate(self,):

        alphabeta = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW"
        num = "0123456789"
        s = ""
        length = random.randint(self.config.MIN_LENGTH, self.config.MAX_LENGTH)

        # if POSSIBILITY_PURE_ENG
        # E:english N:num C:Chinese
        options = ["E", "EN", "EC", "ENC"]
        opt = np.random.choice(options, p=[0.5, 0.2, 0.2, 0.1])


        def sample(charset, length):
            s = ""
            for i in range(length):
                j = random.randint(0, len(charset) - 1)
                s += charset[j]
            return s


        english = sample(alphabeta, length)
        if opt == "E":
            return english

        snum = sample(num, length)
        chinese = sample(self.charset, length)

        if opt == "EN":
            all = list(english + snum)
            np.random.shuffle(all)
            return "".join(all[:length])

        if opt == "EC":
            all = list(english + chinese)
            np.random.shuffle(all)
            return "".join(all[:length])

        if opt == "ENC":
            all = list(english + snum + chinese)
            np.random.shuffle(all)
            return "".join(all[:length])

        raise ValueError("无法识别的Option：%s", opt)