import os,logging,cv2
from crnn.local_utils import data_utils

logger = logging.getLogger("Image Padding")

# 注意：需要在根目录下运行，存到 /data/train目录下
if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--type")

    args = parser.parse_args()

    DATA_DIR = "data"
    TYPE= args.type

    in_dir = os.path.join(DATA_DIR, TYPE)
    if not os.path.exists(in_dir):
        logger.error("目录%s不存在",in_dir)
        exit()

    out_dir = os.path.join(DATA_DIR,TYPE+".pad")
    if not os.path.exists(out_dir):os.makedirs(out_dir)

    for img_name in os.listdir(in_dir):
        image_file = os.path.join(in_dir, img_name)
        logger.debug("padding图像：%s", image_file)
        image = cv2.imread(image_file)
        image = data_utils.padding(image)
        cv2.imwrite(os.path.join(out_dir,img_name),image)


