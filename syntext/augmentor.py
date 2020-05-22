import imgaug as ia
from imgaug import augmenters as iaa
from imgaug import parameters as iap


"""
效果
"""
class Effect():
    def __init__(self):
        pass

    def do(self, other):
        pass


class Augumentor():

    def __init__(self, conf):
        self.conf = conf

    def augument(self, image,pos):
        def do_random(image):
            effects = [
                iaa.Noop(name="origin"),
                iaa.Crop((0, 10)),  # 切边, (0到10个像素采样)
                iaa.GaussianBlur(),
                iaa.AverageBlur(),
                iaa.MedianBlur(),
                iaa.Sharpen(),
                iaa.BilateralBlur(),  # 既噪音又模糊，叫双边,
                iaa.MotionBlur(),
                iaa.MeanShiftBlur(),
                iaa.GammaContrast(),
                iaa.SigmoidContrast(),
                iaa.Affine(shear={'x': (-10, 10), 'y': (-10, 10)}, mode="edge"),
                # shear：x轴往左右偏离的像素书，(a,b)是a,b间随机值，[a,b]是二选一
                iaa.Rotate(rotate=(-10, 10), mode="edge"),
                iaa.PiecewiseAffine(),  # 局部点变形,
                iaa.Fog(),
                iaa.Clouds(),
                iaa.Snowflakes(flake_size=(0.1, 0.2), density=(0.005, 0.025)),
                iaa.Rain(nb_iterations=1, drop_size=(0.05, 0.1), speed=(0.04, 0.08)),
                iaa.ElasticTransformation(alpha=(0.0, 20.0), sigma=(3.0, 5.0), mode="nearest"),
                iaa.AdditiveGaussianNoise(scale=(0, 10)),
                iaa.AdditiveLaplaceNoise(scale=(0, 10)),
                iaa.AdditivePoissonNoise(lam=(0, 10)),
                iaa.Salt((0, 0.02)),
                iaa.Pepper((0, 0.02))]

            seq = iaa.SomeOf((1, 3), children=effects, random_order=True)

            # 多边形测试
            polygons = ia.PolygonsOnImage([ia.Polygon(pos)],shape=image.shape)
            images_aug, polygons_aug = seq(images=[image], polygons=polygons)
            image_after = polygons_aug[0].draw_on_image(images_aug[0], size=2)

            # cv2.imwrite(f"debug/out.jpg", image_after)
            return image_after

        return image,pos