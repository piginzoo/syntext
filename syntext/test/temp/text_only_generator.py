import sys,os,random
sys.path.insert(1,'../ctpn')
from ctpn.data_generator import generator
from crnn.local_utils import data_utils
import cv2,numpy as np
from crnn.data_generator.image_enhance import enhance
import time, random, os
from multiprocessing import Process,Queue

POSSIBILITY_CUT_EDGE = 0.2 # 20%的概率，会缺少个边
MAX_CUT_EDGE = 1           # 最大的边的缺的像素


from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

DEBUG = True

'''
    用来生成crnn的样本，之前写的generator.py已经改名=>crnn_generator.py了，
    原因是ctpn做了类似的事了，就不生产duplicated code了，
    但是由于涉及到另外一个项目，所以在import的时候，可以看到"sys.path.append("../ctpn")"这样诡异代码，望理解，
    言外之意，就是ctpn项目得在上级目录，并且，叫做ctpn的文件夹名字
'''

# 生成一张图片
def create_backgroud_image(all_bg_images, width, height):
    bground = random.choice(all_bg_images)
    # if DEBUG: print("width, height: %d,%d" % (width, height))
    # 在大图上随机产生左上角
    x = random.randint(0,bground.size[0]-width)
    y = random.randint(0,bground.size[1]-height)

    # pixel_sum = np.array(bground).sum()

    retry = 0
    while x<0 or y<0:
        print("[ERROR] 这张图太小了，换一张")
        bground = random.choice(all_bg_images)
        x = random.randint(0, bground.size[0] - width)
        y = random.randint(0, bground.size[1] - height)
        retry += 1
        if retry >= 3:
            print("[ERROR] 尝试3次，无法找到合适的背景，放弃")
            return None,None

    bground = bground.crop((x, y, x+width, y+height))

    # if pixel_sum < 100000000:
    #     print('背景图像素和为:', pixel_sum)
    #     return bground, False
    return bground, True

# 给定一个四边形，得到他的包裹的矩形的宽和高，用来做他的背景图片
def rectangle_w_h(points):
    # if DEBUG: print("points:%r",points)
    x_min,y_min = np.min(points,axis=0)
    x_max,y_max = np.max(points,axis=0)
    # if DEBUG: print("x_min:%f,x_max:%f,y_min:%f,y_max:%f" %(x_min,x_max,y_min,y_max))
    return int(x_max - x_min), int(y_max - y_min)


def create_image(queue,save_path,id,task_num, charset,font_dir,corpus=None):

    all_bg_images = generator.load_all_backgroud_images(os.path.join('data/data_generator/background/'))
    for num in range(task_num):
        try:
            words_image, _, _, random_word, points = generator.create_one_sentence_image(charset,font_dir,corpus)
            # points,返回的是仿射的4个点，不是矩形，是旋转了的
            print("文字：",random_word)
            # 弄一个矩形框包裹他
            width, height = rectangle_w_h(points)
            # print(f'图片尺寸：{width}*{height}')
            height = max(height, 20) # 图片的高度不能过于小，不然字都没了
            # 生成一张背景图片，剪裁好
            background_image, is_normal = create_backgroud_image(all_bg_images,width,height)

            if background_image is None:
                print("[ERROR] 样本字符尝试寻找背景失败，放弃：%s" % random_word)
                continue

            offset = 0
            if np.random.choice([True, False], p=[POSSIBILITY_CUT_EDGE, 1 - POSSIBILITY_CUT_EDGE]):
                offset = random.randint(-MAX_CUT_EDGE,MAX_CUT_EDGE)

            background_image.paste(words_image, (0,offset), words_image)

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

            print("图像：",image_file_name)
            cv2.imwrite(image_full_path,enhance_image)



            # 调试用
            # image_file_name1 = str(id) + "_" + str(num) + '.原.png'
            # image_full_path1 = os.path.join(save_path, image_file_name1)
            # cv2.imwrite(image_full_path1,opencv_image)

            queue.put({'name':image_full_path,'label':random_word})
        except Exception as e:
            print("样本生成发生错误，忽略此错误，继续....",str(e))
            import traceback
            traceback.print_exc()
            continue
    queue.put({'name': None, 'label': None}) # 完成标志


def save_label(queue,worker,label_file_name):
    label_file = open(label_file_name, 'w', encoding='utf-8')
    counter = 0
    while True:
        try:
            data = queue.get()
            image_full_path = data['name']
            label = data['label']

            if image_full_path is None:
                counter+= 1
                if counter >= worker:
                    print("完成了所有的样本生成")
                    break
                else:
                    continue
            label_file.write(image_full_path + " " + label + '\n')
        except Exception as e:
            print("样本保存发生错误，忽略此错误，继续....",str(e))


    label_file.close()

# 注意：需要在根目录下运行，存到 /data/train目录下
if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--type")
    parser.add_argument("--dir")
    parser.add_argument("--num")
    parser.add_argument("--worker")
    parser.add_argument("--charset") #"charset.6883.txt"

    args = parser.parse_args()

    DATA_DIR = args.dir
    TYPE = args.type
    charset_file_name = args.charset
    if not os.path.exists(args.charset):
        print("字符集文件[%s]不存在" % args.charset)
        exit(-1)
    if not os.path.exists(DATA_DIR):os.makedirs(DATA_DIR)
    if not os.path.exists(os.path.join(DATA_DIR,TYPE)): os.makedirs(os.path.join(DATA_DIR,TYPE))
    if not os.path.exists(os.path.join(DATA_DIR,TYPE + '_abnormal')): os.makedirs(os.path.join(DATA_DIR,TYPE + '_abnormal'))

    # 同时生成label，记录下你生成标签文件名
    label_file_name = os.path.join(DATA_DIR,TYPE+".txt")
    total = int(args.num)
    worker = int(args.worker)
    task_num = total // worker # 每个进程应该处理的个数
    # 加载字符集
    charset = data_utils.get_charset(args.charset)
    # 预先加载所有的纸张背景
    # 生成图片数据
    label_dir = os.path.join(DATA_DIR,TYPE)
    # 定义字体路径
    font_dir = "data/data_generator/font/"
    # corpus = open("data/data_generator/corpus.txt",'r').readlines()

    producers = []
    queue = Queue()
    for i in range(worker):
        p = Process(target=create_image, args=(queue,label_dir,i,task_num,charset,font_dir))
        producers.append(p)
        p.start()

    consumer = Process(target=save_label, args=(queue,worker,label_file_name))
    consumer.start()

    print("样本生成完成")