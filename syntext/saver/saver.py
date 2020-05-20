

class Saver():

    def parse_lines(self,data):
        pass

    def save_label(self, queue, worker, label_file_name):
        label_file = open(label_file_name, 'w', encoding='utf-8')
        counter = 0
        while True:
            try:
                data = queue.get()
                image_full_path = data['name']
                label = data['label']

                if image_full_path is None:
                    counter += 1
                    if counter >= worker:
                        print("完成了所有的样本生成")
                        break
                    else:
                        continue
                label_file.write(image_full_path + " " + label + '\n')
            except Exception as e:
                print("样本保存发生错误，忽略此错误，继续....", str(e))

        label_file.close()


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
class ContourSaver(Saver):
    def _bbox2str(self,bbox):
        return ""

    def parse_lines(self,data):
        lines = []
        lines.append(data['label'])
        for bbox in data['pos']:
            lines.append(self._bbox2str(bbox))
        return lines
