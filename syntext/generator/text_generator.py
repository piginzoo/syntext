from syntext.generator.generator import Generator
import os

class TextOnlyGenerator(Generator):
    """
    标注文件样例：
    ```text
    data/train/abc.jpg 你好，世界
    data/train/bcd.jpg 毁灭吧，世界！累了~
    ......
    ```
    """

    def __init__(self, config, charset, fonts, backgrounds, text_creator, augmentor):
        super().__init__(config, charset, fonts, backgrounds, text_creator, augmentor)

    def build_label_data(self, text, char_bboxes):
        return text

    def get_label_name(self, image_path):
        dir,_ = os.path.split(image_path)
        label_file_path = os.path.join(dir, "train.txt")
        return label_file_path

    def parse_lines(self, image_path, label):
        return [image_path + " " + label]
