import numpy as np


class TextCreator():
    """
    用于生成一个完整的字符串，会组合各种文本生成器（generator）
    组合的概率来自原配置文件[config.yml](config.yml)
    """
    def _random_accept(accept_possibility):
        return np.random.choice([True, False], p=[accept_possibility, 1 - accept_possibility])

    def generate(self):
        raise NotImplementedError("子类事先")
