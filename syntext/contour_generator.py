from syntext.generator import Generator
from syntext.saver.saver import ContourSaver
from syntext.text.text_creator import RandomTextGenerator
from syntext.augment.augmentor import Augumentor
from PIL import Image, ImageDraw, ImageFont


"""
会对每一个字进行标注，使用四点标注法。
"""
class ContourGenerator(Generator):
    def __init__(self, config, charset, fonts, backgrounds):
        super().__init__(self, config, charset, fonts, backgrounds)
        self.text_creator = RandomTextGenerator(config)
        self.saver = ContourSaver(config)
        self.augmentor = Augumentor(config)

    def create_one_sentence_image(self):

        text = self.text_creator.generate()
        font,color = self.choose_font()
        background = self.choose_backgournd()

        # 因为有数字啊，英文字母啊，他的宽度比中文短，所以为了框套的更严丝合缝，好好算算宽度
        width, height = self._caculate_text_shape(text,font)

        image = Image.new('RGBA', (width, height-e))
        draw = ImageDraw.Draw(image)
        # 注意下，下标是从0,0开始的，是自己的坐标系
        draw.text((0, 0), text, fill=color, font=font)

        image, label_data = self.augmentor.augument(image)

        self.saver.save(image,label_data)

    def create_image(queue, save_path, id, task_num, charset, font_dir, corpus=None):
        words_image, _, _, random_word, points = generator.create_one_sentence_image(charset, font_dir, corpus)
        # points,返回的是仿射的4个点，不是矩形，是旋转了的
        print("文字：", random_word)
        # 弄一个矩形框包裹他
        width, height = rectangle_w_h(points)
        # print(f'图片尺寸：{width}*{height}')
        height = max(height, 20)  # 图片的高度不能过于小，不然字都没了
        # 生成一张背景图片，剪裁好
        background_image, is_normal = create_backgroud_image(all_bg_images, width, height)

        if background_image is None:
            print("[ERROR] 样本字符尝试寻找背景失败，放弃：%s" % random_word)
            continue

        offset = 0
        if np.random.choice([True, False], p=[POSSIBILITY_CUT_EDGE, 1 - POSSIBILITY_CUT_EDGE]):
            offset = random.randint(-MAX_CUT_EDGE, MAX_CUT_EDGE)

        background_image.paste(words_image, (0, offset), words_image)

        opencv_image = cv2.cvtColor(np.asarray(background_image), cv2.COLOR_RGB2BGR)

        h, w, _ = opencv_image.shape
        scale = 32 / h
        opencv_image = cv2.resize(opencv_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        enhance_image = enhance(opencv_image, phase='generation')

        # 保存文本信息和对应图片名称
        image_file_name = str(id) + "_" + str(num) + '.png'

        if not is_normal:  # 异常图片保存在另外一个文件夹
            image_full_path = os.path.join(save_path + '_abnormal', image_file_name)
        else:
            image_full_path = os.path.join(save_path, image_file_name)

        print("图像：", image_file_name)
        cv2.imwrite(image_full_path, enhance_image)
