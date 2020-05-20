import time,random
from syntext.utils.utils import date_formatter
from syntext.text.generator import TextGenerator

class SingleGenerator(TextGenerator):
    def __init__(self, config, charset):
        super().__init__("single",config)

    def generate(self):
        now = time.time()

        _format = random.choice(date_formatter)

        _timestamp = random.uniform(0, now)

        time_local = time.localtime(_timestamp)

        return time.strftime(_format, time_local)