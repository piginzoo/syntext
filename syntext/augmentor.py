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
        seq = iaa.Sequential([
            # 变形
            iaa.Sometimes(0.6, [
                iaa.OneOf([
                    iaa.Affine(shear={'x': (-1.5, 1.5), 'y': (-1.5, 1.5)}, mode="edge"),# 仿射变化程度，单位像素
                    iaa.Rotate(rotate=(-1, 1), mode="edge"),  # 旋转,单位度
                ])
            ]),
            # 扭曲
            iaa.Sometimes(0.5,[
                iaa.OneOf([
                    iaa.PiecewiseAffine(scale=(0,0.02), nb_rows=2, nb_cols=2),  # 局部仿射
                    iaa.ElasticTransformation(  # distort扭曲变形
                        alpha=(0,3), # 扭曲程度
                        sigma=(0.8,1), # 扭曲后的平滑程度
                        mode="nearest"),
                    iaa.GaussianBlur(sigma=(0,0.7)),
                    iaa.AverageBlur(k=(1,3)),
                    iaa.MedianBlur(k=(1,3)),
                    iaa.BilateralBlur(d=(1,5), sigma_color=(10,200), sigma_space=(10,200)),  # 既噪音又模糊，叫双边,
                    iaa.MotionBlur(k=(3,5)),
                    iaa.Snowflakes(flake_size=(0.1, 0.2), density=(0.005, 0.025)),
                    iaa.Rain(nb_iterations=1, drop_size=(0.05, 0.1), speed=(0.04, 0.08)),
                ])
            ]),
            # 锐化
            iaa.Sometimes(0.3,[
                    iaa.OneOf([
                    iaa.Sharpen(),
                    iaa.GammaContrast(),
                    iaa.SigmoidContrast()
                ])
            ]),
            # 噪音
            iaa.Sometimes(0.3,[
                iaa.OneOf([
                    iaa.AdditiveGaussianNoise(scale=(1,5)),
                    iaa.AdditiveLaplaceNoise(scale=(1,5)),
                    iaa.AdditivePoissonNoise(lam=(1,5)),
                    iaa.Salt((0, 0.02)),
                    iaa.Pepper((0, 0.02))
                ])
            ]),
            # 剪切
            iaa.Sometimes(0.8,[
                    iaa.OneOf([
                    iaa.Crop((0, 2)),  # 切边, (0到10个像素采样)
                ])
            ]),
        ])

        polys = [ia.Polygon(pos) for pos in bbox_list]
        polygons = ia.PolygonsOnImage(polys, shape=image.shape)
        # 处理部分或者整体出了图像的范围的多边形，参考：https://imgaug.readthedocs.io/en/latest/source/examples_bounding_boxes.html
        polygons = polygons.remove_out_of_image().clip_out_of_image()
        images_aug, polygons_aug = seq(images=[image], polygons=polygons)
        image = images_aug[0]

        new_polys = []
        for p in polygons_aug.polygons:
            new_polys.append(p.coords)
        polys = np.array(new_polys, np.int32).tolist()

        return image, polys
