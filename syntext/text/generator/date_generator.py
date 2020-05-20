import time,random
from syntext.text.text_generator import TextGenerator

class DateGenerator(TextGenerator):
    def __init__(self):
        super().__init__("date")

    def generate(self):
        now = time.time()

        # 准备各种各样的日期格式，随机挑一个
        date_formatter = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%Y%m%d ",
            "%y-%m-%d ",
            "%y/%m/%d ",
            "%y年%m月%d日",
            "%Y%m%d "
        ]

        _format = random.choice(date_formatter)

        _timestamp = random.uniform(0, now)

        time_local = time.localtime(_timestamp)

        return time.strftime(_format, time_local)