from syntext.saver.saver import Saver
import numpy as np
import os

class ContourSaver(Saver):
    """
    标注文件样例：
    ```text
        你好，世界                      <---- 第1行，标注结果
        11,12,21,22,31,32,41,42 你     <---- 第2行-最后一行，标注每个文字的框
        11,12,21,22,31,32,41,42 好
        11,12,21,22,31,32,41,42 ，
        11,12,21,22,31,32,41,42 世
        11,12,21,22,31,32,41,42 界
    ```
    """

    def __init__(self, conf):
        self.conf = conf

    # {
    #   "label":"你好世界！",
    #   "pos":[
    #       {
    #           "bbox": [[x1,y1],[x1,y1],[x1,y1],[x1,y1]],
    #           "word": "你"
    #       },
    #       ....
    #   ]
    # }
    #
    # ======>
    #
    #   你好，世界
    #   11,12,21,22,31,32,41,42,你
    #   11,12,21,22,31,32,41,42,好
    #   ....
    #
    # 说明：8个坐标和最后汉字都用逗号分割，避免空格引起的歧义
    #
    # pos:{'word':'你',bbox:<4,2>}
    def _bbox2str(self, pos):
        import logging

        word = pos['word']
        bbox = pos['bbox']  # [4,2]

        if type(bbox) == list: bbox = np.array(bbox)

        assert bbox.shape == (4, 2)

        bbox_list = bbox.reshape(-1).tolist()
        logging.debug("bbox:%r", bbox_list)

        bbox_list = ",".join(str(p) for p in bbox_list)

        return bbox_list + "," + word

    def get_label_name(self, image_path):
        name, ext = os.path.splitext(image_path)
        label_file_path = name + ".txt"
        return label_file_path

    def parse_lines(self, image_path, label):
        lines = []
        lines.append(label['label'])
        for pos in label['pos']:  # pos:{'word':'你',bbox:<4,2>}
            lines.append(self._bbox2str(pos))
        return lines
