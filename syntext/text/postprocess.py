import numpy as np

# 做字符串的后处理
class PostProcessor():
    def __init__(self, name, config):
        self.name = name
        self.config = config

    def process(self,text):
        raise NotImplementedError("子类实现")

    def is_accept(self,possible):
        return np.random.choice([True,False], p = [possible,1 - possible])
