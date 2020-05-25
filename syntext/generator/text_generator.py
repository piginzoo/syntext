from syntext.generator.generator import Generator


class TextOnlyGenerator(Generator):
    """
    标注文件样例：
    ```text
    data/train/abc.jpg 你好，世界
    data/train/bcd.jpg 毁灭吧，世界！累了~
    ......
    ```
    """

    def __init__(self, conf):
        self.conf = conf

    def get_label_name(self, image_path):
        return "train.txt"

    def parse_lines(self, image_path, label):
        return image_path + " " + label
