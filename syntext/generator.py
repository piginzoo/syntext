from multiprocessing import Process,Queue
import os,random
import numpy as np

class Generator():
    def __init__(self, config, charset, fonts, backgrounds):
        self.config = config
        self.worker = config.COMMON['WORKER']
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

    # 生成一张图片
    def choose_backgournd(self, width, height):
        bground = random.choice(self.backgrounds)
        x = random.randint(0, bground.size[0] - width)
        y = random.randint(0, bground.size[1] - height)
        retry = 0
        while x < 0 or y < 0:
            print("[ERROR] 这张图太小了，换一张")
            bground = random.choice(self.backgrounds)
            x = random.randint(0, bground.size[0] - width)
            y = random.randint(0, bground.size[1] - height)
            retry += 1
            if retry >= 5:
                print("[ERROR] 尝试5次，无法找到合适的背景，放弃")
                return None

        bground = bground.crop((x, y, x + width, y + height))
        return bground

    def charset(self):
        pass

    def _create_image(self,queue,num):
        image, data = self.create_image(num)
        queue.put({'image':image, 'data':data})

    def _save_label(self, queue, total_num):
        counter = 0
        while True:
            try:
                data = queue.get()
                image = data['image']
                label = data['label']

                if image is None:
                    counter += 1
                    if counter >= total_num:
                        print("完成了所有的样本生成")
                        break
                    else:
                        continue
                self.saver.save(image,label)
            except Exception as e:
                print("样本保存发生错误，忽略此错误，继续....", str(e))

    def create_image(self,num):
        raise NotImplementedError("需要子类化")

    def save_label(self,label_data):
        raise NotImplementedError("需要子类化")

    def execute(self,total_num):
        producers = []
        queue = Queue()
        num = total_num//self.worker
        for i in range(self.worker):
            p = Process(target=self._create_image, args=(queue,num,))
            producers.append(p)
            p.start()

        consumer = Process(target=self._save_label, args=(queue,total_num))
        consumer.start()

        print("样本生成完成")