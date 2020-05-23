import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa


class Augumentor():
    """
    图像增强
    """

    def __init__(self, conf):
        self.conf = conf

    # bbox_list: is list of list, shape is [4,2]
    def augument(self, image, bbox_list):

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

        polys = [ia.Polygon(pos) for pos in bbox_list]
        polygons = ia.PolygonsOnImage(polys, shape=image.shape)
        images_aug, polygons_aug = seq(images=[image], polygons=polygons)
        image = images_aug[0]

        return image, polygons_aug
