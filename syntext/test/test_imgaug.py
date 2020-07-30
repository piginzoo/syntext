import cv2
import os
import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa


def do_aug(image, aug):
    seq = iaa.Sequential([
        aug
    ])

    # 测试bbox变形，不过放弃了，因为bbox始终是水平的，即使是做了仿射，还是水平的，改用下面的多边形测试了
    # seq_det = seq.to_deterministic()  # 保持坐标和图像同步改变，而不是随机
    # bbox的测试
    # bbs = ia.BoundingBoxesOnImage(
    # [
    #     ia.BoundingBox(x1=20, y1=70, x2=110, y2=130)
    # ], shape=image.shape)
    # image_aug = seq_det.augment_images([image])[0]
    # bbs_aug = seq_det.augment_polygons([bbs])[0]
    # image_aug = seq_det.augment_images([image])[0]
    # bbs_aug = seq_det.augment_polygons(polygons)[0]

    # 多边形测试
    polygons = ia.PolygonsOnImage([
        ia.Polygon(
            [(20, 70),
             (110, 70),
             (110, 130),
             (20, 130)])],
        shape=image.shape)
    images_aug, polygons_aug = seq(images=[image], polygons=polygons)
    image_after = polygons_aug[0].draw_on_image(images_aug[0], size=2)

    cv2.imwrite(f"debug/{aug.name}.jpg", image_after)
    return image_after


# 固定测试每种效果
# 参考：https://imgaug.readthedocs.io/en/latest/source/api_imgaug.html
def do_all_aug(image):
    do_aug(image, iaa.Noop(name="origin"))
    do_aug(image, iaa.Crop((0, 10)))  # 切边
    do_aug(image, iaa.GaussianBlur((0, 3)))
    do_aug(image, iaa.AverageBlur(1, 7))
    do_aug(image, iaa.MedianBlur(1, 7))
    do_aug(image, iaa.Sharpen())
    do_aug(image, iaa.BilateralBlur())  # 既噪音又模糊，叫双边
    do_aug(image, iaa.MotionBlur())
    do_aug(image, iaa.MeanShiftBlur())
    do_aug(image, iaa.GammaContrast())
    do_aug(image, iaa.SigmoidContrast())
    do_aug(image,
           iaa.Affine(shear={'x': (-10, 10), 'y': (-10, 10)}, mode="edge"))  # shear：x轴往左右偏离的像素书，(a,b)是a,b间随机值，[a,b]是二选一
    do_aug(image,
           iaa.Affine(shear={'x': (-10, 10), 'y': (-10, 10)}, mode="edge"))  # shear：x轴往左右偏离的像素书，(a,b)是a,b间随机值，[a,b]是二选一
    do_aug(image, iaa.Rotate(rotate=(-10, 10), mode="edge"))
    do_aug(image, iaa.PiecewiseAffine())  # 局部点变形
    do_aug(image, iaa.Fog())
    do_aug(image, iaa.Clouds())
    do_aug(image, iaa.Snowflakes(flake_size=(0.1, 0.2), density=(0.005, 0.025)))
    do_aug(image, iaa.Rain(nb_iterations=1, drop_size=(0.05, 0.1), speed=(0.04, 0.08), ))
    do_aug(image, iaa.ElasticTransformation(alpha=(0.0, 20.0), sigma=(3.0, 5.0), mode="nearest"))
    do_aug(image, iaa.AdditiveGaussianNoise(scale=(0, 10)))
    do_aug(image, iaa.AdditiveLaplaceNoise(scale=(0, 10)))
    do_aug(image, iaa.AdditivePoissonNoise(lam=(0, 10)))
    do_aug(image, iaa.Salt((0, 0.02)))
    do_aug(image, iaa.Pepper((0, 0.02)))


# 随机选的例子
def do_aug_random(image):
    seq = iaa.SomeOf(
        n=(1, 3),
        random_order=True,
        children=[
            iaa.Crop(px=(0, 16)),  # crop images from each side by 0 to 16px (randomly chosen)
            iaa.Fliplr(0.5),  # horizontally flip 50% of the images
            iaa.GaussianBlur(sigma=(0, 3.0))  # blur images with a sigma of 0 to 3.0
        ])
    images_augs = seq(images=[image])
    for o in images_augs:
        cv2.imwrite("debug/out.jpg", o)
    return images_augs


def do_random(image, pos_list):
    # 1.先任选5种影响位置的效果之一做位置变换
    seq = iaa.Sequential([
        iaa.Sometimes(0.5, [
            iaa.Crop((0, 10)),  # 切边, (0到10个像素采样)
        ]),
        iaa.Sometimes(0.5, [
            iaa.Affine(shear={'x': (-10, 10), 'y': (-10, 10)}, mode="edge"),
            iaa.Rotate(rotate=(-10, 10), mode="edge"),  # 旋转
        ]),
        iaa.Sometimes(0.5, [
            iaa.PiecewiseAffine(),  # 局部仿射
            iaa.ElasticTransformation(  # distort扭曲变形
                alpha=(0.0, 20.0),
                sigma=(3.0, 5.0),
                mode="nearest"),
        ]),
        # 18种位置不变的效果
        iaa.SomeOf((1, 3), [
            iaa.GaussianBlur(),
            iaa.AverageBlur(),
            iaa.MedianBlur(),
            iaa.Sharpen(),
            iaa.BilateralBlur(),  # 既噪音又模糊，叫双边,
            iaa.MotionBlur(),
            iaa.MeanShiftBlur(),
            iaa.GammaContrast(),
            iaa.SigmoidContrast(),
            iaa.Fog(),
            iaa.Clouds(),
            iaa.Snowflakes(flake_size=(0.1, 0.2), density=(0.005, 0.025)),
            iaa.Rain(nb_iterations=1, drop_size=(0.05, 0.1), speed=(0.04, 0.08)),
            iaa.AdditiveGaussianNoise(scale=(0, 10)),
            iaa.AdditiveLaplaceNoise(scale=(0, 10)),
            iaa.AdditivePoissonNoise(lam=(0, 10)),
            iaa.Salt((0, 0.02)),
            iaa.Pepper((0, 0.02))
        ])
    ])

    polys = [ia.Polygon(pos) for pos in pos_list]
    polygons = ia.PolygonsOnImage(polys, shape=image.shape)
    images_aug, polygons_aug = seq(images=[image], polygons=polygons)
    image = images_aug[0]
    image = polygons_aug.draw_on_image(image, size=2)

    new_polys = []
    for p in polygons_aug.polygons:
        new_polys.append(p.coords)
    polys = np.array(new_polys, np.int32).tolist()

    return image, polys


if __name__ == '__main__':

    if not os.path.exists("debug"): os.mkdir("debug")
    image = cv2.imread("zoo.jpg")
    # do_all_aug(image)
    pos = [
        [(20, 70), (110, 70), (110, 130), (20, 130)],
        [(55, 15), (85, 15), (85, 45), (55, 45)]
    ]
    image, polys = do_random(image, pos)
    cv2.imwrite("debug/out.jpg", image)
    print(polys)
