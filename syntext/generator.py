from multiprocessing import Process,Queue
import os,random
import numpy as np

class Generator():
    def __init__(self, config, charset, fonts, backgrounds):
        self.config = config
        self.charset = charset
        self.fonts = fonts
        self.backgrounds = backgrounds

    # 因为英文、数字、符号等ascii可见字符宽度短，所以要计算一下他的实际宽度，便于做样本的时候的宽度过宽
    def _caculate_text_shape(text, font):
        # 获得文件的大小,font.getsize计算的比较准
        width, height = font.getsize(text)
        return width, height

    # 产生随机颜色, 各通道小于
    def _get_random_color(self):
        base_color = random.randint(0, 128)
        noise_r = random.randint(0, 100)
        noise_g = random.randint(0, 100)
        noise_b = random.randint(0, 100)
        noise = np.array([noise_r, noise_g, noise_b])
        font_color = (np.array(base_color) + noise).tolist()
        return tuple(font_color)

    def choose_font(self):
        font_color = self._get_random_color()
        return random.choice(self.backgrounds),font_color

    def choose_backgournd(self):
        return random.choice(self.backgrounds)

    def charset(self):
        pass

    def create_image(queue, save_path, id, task_num, charset, font_dir, corpus=None):
        pass

    def generate_label(self,file_name,label):
        f = open(file_name,"a")
        f.write(file_name)
        f.write(" ")
        f.write(label)
        f.close()

    def get_worker(self):
        return 1

    def execute(self):
        producers = []
        queue = Queue()
        for i in range(self.get_worker()):
            p = Process(target=self.create_image, args=(queue, label_dir, i, task_num, charset, font_dir))
            producers.append(p)
            p.start()

        consumer = Process(target=save_label, args=(queue, worker, label_file_name))
        consumer.start()

        print("样本生成完成")