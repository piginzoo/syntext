import random,cv2,math
import Augmentor.Operations as aug
import PIL
from PIL import Image, ImageDraw
import numpy as np

def rotate_img(image, degree):
    img = np.array(image)

    height, width = img.shape[:2]

    heightNew = int(width * math.fabs(math.sin(math.radians(degree))) + height * math.fabs(math.cos(math.radians(degree))))
    widthNew = int(height * math.fabs(math.sin(math.radians(degree))) + width * math.fabs(math.cos(math.radians(degree))))

    matRotation = cv2.getRotationMatrix2D((width / 2, height / 2), degree, 1)

    matRotation[0, 2] += (widthNew - width) / 2  
    matRotation[1, 2] += (heightNew - height) / 2  
    
    imgRotation = cv2.warpAffine(img, matRotation, (widthNew, heightNew), borderValue=(255, 255, 255, 0))

    w = width
    h = height

    points = np.matrix([[-w / 2, -h / 2, 1], [-w / 2, h / 2, 1], [w / 2, h / 2, 1], [w / 2, -h / 2, 1]])

    matRotation = cv2.getRotationMatrix2D((w / 2, h / 2), degree, 1)

    matRotation[0, 2] = widthNew / 2
    matRotation[1, 2] = heightNew / 2

    p = matRotation * points.T

    # for row in imgRotation:
    #     for element in row:
    #         print(element)
    #         if element[3] == 0:
    #             for i in xrange(3):
    #                 element[i] = 0
    image = Image.fromarray(imgRotation)
    points = np.array(p.T, int)
    return image, points

def main(txt_img, points):
    # Augment rate for eatch type
    rot = random.uniform(0, 1)
    skew_rate = random.uniform(0, 1)
    shear_rate = random.uniform(0, 1)
    distort_rate = random.uniform(0, 1)
    
    
    rot_degree = random.randint(-10, 10)
    txt_img, points = rotate_img(txt_img, rot_degree)
    # 平行四边形形变
    skew = aug.Skew(1, 'RANDOM', 0.5)
    txt_img = skew.perform_operation([txt_img])
    # 剪切形变
    shear= aug.Shear(1., 5, 5)
    txt_img = shear.perform_operation(txt_img)
    # 扭曲变形
    distort = aug.Distort(1.0, 100, 10, 1)
    txt_img = distort.perform_operation(txt_img)
    return txt_img

if __name__ == '__main__':
    image = Image.open("zoo1.jpg")
    out = main(image,None)
    for o in out:
        o.save("out.jpg")
