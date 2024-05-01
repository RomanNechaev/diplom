import numpy as np
from SSIM_PIL import compare_ssim
from PIL import Image
import cv2
import lpips
import torch
import numpy as np


class Metrics:
    @staticmethod
    def mse(image_a, image_b):
        image_a = cv2.imread(image_a)
        image_b = cv2.imread(image_b)
        err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
        err /= float(image_a.shape[0] * image_a.shape[1])

        return err

    @staticmethod
    def ssim(image_a, image_b):
        image1 = Image.open(image_a)
        image2 = Image.open(image_b)
        return compare_ssim(image1,image2)

    @staticmethod
    def lpips(image_a, image_b):
        loss_fn = lpips.LPIPS(net='alex')
        first = lpips.im2tensor(lpips.load_image(image_a))
        second = lpips.im2tensor(lpips.load_image(image_b))
        lpips_metric = loss_fn.forward(first, second)
        return lpips_metric
