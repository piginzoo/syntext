import cv2
import os
import imgaug as ia
from imgaug import augmenters as iaa


def do_aug(image, aug):
    seq = iaa.Sequential([
        aug
    ])

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

    # 多边形box测试
    polygons = ia.PolygonsOnImage([
                    ia.Polygon(
                           [(20,70),
                            (110,70),
                            (110,130),
                            (20,130)])],
                    shape=image.shape)
    images_aug, polygons_aug = seq(images=[image], polygons=polygons)
    image_after = polygons_aug[0].draw_on_image(images_aug[0], size=2)

    cv2.imwrite(f"debug/{aug.name}.jpg", image_after)

# 固定测试每种效果
def do_all_aug(image):

    do_aug(image, iaa.Crop(px=10))  # 切边
    do_aug(image, iaa.GaussianBlur(sigma=(0, 3.0)))
    do_aug(image, iaa.AverageBlur())
    do_aug(image, iaa.MedianBlur())
    do_aug(image, iaa.Sharpen())
    do_aug(image, iaa.BilateralBlur())
    do_aug(image, iaa.MotionBlur())
    do_aug(image, iaa.MeanShiftBlur())
    do_aug(image, iaa.GammaContrast())
    do_aug(image, iaa.SigmoidContrast())
    do_aug(image, iaa.Affine())
    do_aug(image, iaa.Rotate())
    do_aug(image, iaa.PiecewiseAffine())
    do_aug(image, iaa.Fog())
    do_aug(image, iaa.ElasticTransformation(alpha=50.0, sigma=5.0))

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


if __name__ == '__main__':

    if not os.path.exists("debug"): os.mkdir("debug")
    image = cv2.imread("zoo.jpg")
    do_all_aug(image)
