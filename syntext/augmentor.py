import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa


class Augumentor():
    """
    图像增强，使用了[imgaug](https://imgaug.readthedocs.io/)。
    采用了Sequential（串行）来组合:
    - 变形: 0.6
    - 扭曲: 0.5
    - 锐化: 0.3
    - 噪音: 0.3
    - 剪切: 0.8
    第二列为每种增强的实施概率，
    设计上使用Sometimes+OneOf，来实现1/N，直接使用Sometimes会导致他的list所有的效果都执行，因此必须组合OneOf
    各种参数都经过了微调，专门针对文字图片生成，尝试之后删除了某些不合适的效果，目前是最佳的一些组合
    最终返回增强后的图像，和被变形后的文字多边形
    """

    def __init__(self, conf):
        self.conf = conf

    # bbox_list: is list of list, shape is [4,2]
    def augument(self, image, bbox_list):
        seq = iaa.Sequential([
            # 变形
            iaa.Sometimes(0.6, [
                iaa.OneOf([
                    iaa.Affine(shear={'x': (-1.5, 1.5), 'y': (-1.5, 1.5)}, mode="edge"),  # 仿射变化程度，单位像素
                    iaa.Rotate(rotate=(-1, 1), mode="edge"),  # 旋转,单位度
                ])
            ]),
            # 扭曲
            iaa.Sometimes(0.5, [
                iaa.OneOf([
                    iaa.PiecewiseAffine(scale=(0, 0.02), nb_rows=2, nb_cols=2),  # 局部仿射
                    iaa.ElasticTransformation(  # distort扭曲变形
                        alpha=(0, 3),  # 扭曲程度
                        sigma=(0.8, 1),  # 扭曲后的平滑程度
                        mode="nearest"),
                    iaa.GaussianBlur(sigma=(0, 0.7)),
                    iaa.AverageBlur(k=(1, 3)),
                    iaa.MedianBlur(k=(1, 3)),
                    iaa.BilateralBlur(d=(1, 5), sigma_color=(10, 200), sigma_space=(10, 200)),  # 既噪音又模糊，叫双边,
                    iaa.MotionBlur(k=(3, 5)),
                    iaa.Snowflakes(flake_size=(0.1, 0.2), density=(0.005, 0.025)),
                    iaa.Rain(nb_iterations=1, drop_size=(0.05, 0.1), speed=(0.04, 0.08)),
                ])
            ]),
            # 锐化
            iaa.Sometimes(0.3, [
                iaa.OneOf([
                    iaa.Sharpen(),
                    iaa.GammaContrast(),
                    iaa.SigmoidContrast()
                ])
            ]),
            # 噪音
            iaa.Sometimes(0.3, [
                iaa.OneOf([
                    iaa.AdditiveGaussianNoise(scale=(1, 5)),
                    iaa.AdditiveLaplaceNoise(scale=(1, 5)),
                    iaa.AdditivePoissonNoise(lam=(1, 5)),
                    iaa.Salt((0, 0.02)),
                    iaa.Pepper((0, 0.02))
                ])
            ]),
            # 剪切
            iaa.Sometimes(0.8, [
                iaa.OneOf([
                    iaa.Crop((0, 2)),  # 切边, (0到10个像素采样)
                ])
            ]),
        ])

        assert bbox_list is None or type(bbox_list) == list

        if bbox_list is None or len(bbox_list) == 0:
            polys = None
        else:
            polys = [ia.Polygon(pos) for pos in bbox_list]
            polys = ia.PolygonsOnImage(polys, shape=image.shape)

        # 处理部分或者整体出了图像的范围的多边形，参考：https://imgaug.readthedocs.io/en/latest/source/examples_bounding_boxes.html
        polys = polys.remove_out_of_image().clip_out_of_image()
        images_aug, polygons_aug = seq(images=[image], polygons=polys)

        image = images_aug[0]

        if polygons_aug is None:
            polys = None
        else:
            polys = []
            for p in polygons_aug.polygons:
                polys.append(p.coords)
            polys = np.array(polys, np.int32).tolist()

        return image, polys
