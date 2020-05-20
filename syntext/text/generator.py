import random

class TextGenerator():
    def __init__(self, name, config):
        self.name = name
        self.config = config

    def _random_accept(accept_possibility):
        return np.random.choice([True,False], p = [accept_possibility,1 - accept_possibility])

    def generate(self):
        raise NotImplementedError("子类实现")