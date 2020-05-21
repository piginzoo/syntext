import random
import numpy as np
from syntext.utils.utils import dynamic_load
from syntext.text.generator import TextGenerator
from syntext.text.postprocess import PostProcessor


class TextCreator():
    def __init__(self):
        pass

    def _random_accept(accept_possibility):
        return np.random.choice([True, False], p=[accept_possibility, 1 - accept_possibility])

    def generate(self):
        pass


"""
根据字库随机生成概率定制生成策略，生成随机文本的文本生成器
# - 左右留白
# - 加大纯英文比例
# - 加大英文和数字的比例
# - 增加一些变形情况
# - 增加别的上面或者下面出现一半的文字的干扰
# - 增加左右留白的，解决符号的问题
# - 增加纯英文，英文数字混合、英文汉字混合、英文数字汉字混合的，解决英文识别效果差的问题
# - 增加变形后，上下会有
"""


class RandomTextGenerator(TextCreator):
    def __init__(self, config, charset):
        self.config = config
        self.charset = charset
        self.generaters = {}
        self.post_processors = {}

        self._initialize_generators()
        self._initialize_post_processors()

    def _initialize_generators(self):
        classes = dynamic_load("syntext.text.generators", TextGenerator)
        for clazz in classes:
            obj = clazz(self.config, self.charset)
            self.generaters[obj.name] = obj

    def _initialize_post_processors(self):
        classes = dynamic_load("syntext.text.postprocesses", PostProcessor)
        for clazz in classes:
            obj = clazz(self.config)
            self.post_processors[obj.name] = obj


    def _normalize_possibility(self, possibility):
        possibility_names = []
        possibility_probabilities = []

        sum = 0

        for name, value in possibility.items():
            possibility_names.append(name)
            possibility_probabilities.append(value)
            sum += value
        possibility_probabilities = [p / sum for p in possibility_probabilities]

        return possibility_names, possibility_probabilities

    # 只在头尾加入空格
    def _generate_blanks_only_head_tail(self, chars):
        # 随机前后加上一些空格
        _blank_num1 = random.randint(1, self.config.MAX_BLANK_NUM)
        _blank_num2 = random.randint(1, self.config.MAX_BLANK_NUM)
        return (" " * _blank_num1) + chars + (" " * _blank_num2)

    def generate(self):
        policy = self.config.POSSIBILITY_TEXT  # POSSIBILITY_TEXT是用于生成
        # 归一化一下
        policy_names, policy_probabilities = self._normalize_possibility(policy)
        generator_name = np.random.choice(policy_names, p=policy_probabilities)
        generator = self.generaters[generator_name]
        text = generator.generate()

        for _,post_processor in self.post_processors.items():
            text = post_processor.process(text)

        return text


"""
基于语料的文本生成器
"""


class CorpusTextGenerator(TextCreator):
    def __init__(self):
        pass
