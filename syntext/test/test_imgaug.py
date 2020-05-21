import cv2
import os
from imgaug import augmenters as iaa


def do_aug(image, aug):
    seq = iaa.Sequential([
        aug
    ])
    images_augs = seq(images=[image])
    cv2.imwrite(f"debug/{aug.name}.jpg", images_augs[0])


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

    if os.path.exists("debug"): os.mkdir("debug")
    image = cv2.imread("zoo.jpg")
    do_all_aug(image)
