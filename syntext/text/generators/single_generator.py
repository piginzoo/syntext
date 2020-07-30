import random
from syntext.text.generator import TextGenerator


class SingleGenerator(TextGenerator):
    def __init__(self, config, charset):
        super().__init__("single", config)
        self.charset = charset

    def generate(self):
        index = random.randint(0, len(self.charset) - 1)
        return self.charset[index]
