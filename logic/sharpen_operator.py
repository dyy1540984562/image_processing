import numpy as np
import cv2

class ImageSharpening:
    def sharpen(self, image):
        pass
# （拉普拉斯锐化）算子：
class LaplacianSharpeningOne(ImageSharpening):
    def sharpen(self, image, sharpenFactor):
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(image, -1, sharpenFactor * kernel)
        return sharpened

class LaplacianSharpeningTwo(ImageSharpening):
    def sharpen(self, image, sharpenFactor):
        kernel = np.array([[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(image, -1, sharpenFactor * kernel)
        return sharpened

class LaplacianSharpeningThree(ImageSharpening):
    def sharpen(self, image, sharpenFactor):
        kernel = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(image, -1, sharpenFactor * kernel)
        return sharpened

# （高提升锐化）算子：
class UnsharpMasking(ImageSharpening):
    def sharpen(self, image, sharpenFactor):
        k = 1 # 控制着高频成分的比例
        blur = cv2.GaussianBlur(image, (0, 0), sharpenFactor)  # 首先对图像进行高斯模糊
        sharpened = cv2.addWeighted(image, 1.5, blur, -0.5, 0) # 通过对原始图像和模糊图像加权求和
        return sharpened
# （斜导数锐化）算子：
class ScharrSharpening(ImageSharpening):
    def sharpen(self, img, sharpenFactor):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scharr_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
        scharr_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)

        sharpened_r = cv2.addWeighted(img[:, :, 2].astype(float), 0.5, scharr_x.astype(float), 0.5, 0)  # 对红色通道进行锐化
        sharpened_g = cv2.addWeighted(img[:, :, 1].astype(float), 0.5, scharr_y.astype(float), 0.5, 0)  # 对绿色通道进行锐化
        sharpened_b = cv2.addWeighted(img[:, :, 0].astype(float), 0.5, scharr_x.astype(float), 0.5, 0)  # 对蓝色通道进行锐化

        sharpened_img = cv2.merge((sharpened_b, sharpened_g, sharpened_r))  # 将通道合并
        return sharpened_img

class ImageSharpeningFactory:
    @staticmethod
    def create_sharpening_instance(type):
        if type == 'laplacian1':
            return LaplacianSharpeningOne()
        elif type == 'laplacian2':
            return LaplacianSharpeningTwo()
        elif type == 'laplacian3':
            return LaplacianSharpeningThree()
        elif type == 'unsharp':
            return UnsharpMasking()
        elif type == 'scharr':
            return ScharrSharpening()
        else:
            raise ValueError('Invalid sharpening type')


# 在示例中应用工厂模式
# sharpening_type = 'laplacian'  # 可以更改为'unsharp'或'scharr'
# image = cv2.imread('image.jpg', cv2.IMREAD_COLOR)

# sharpening_instance = ImageSharpeningFactory.create_sharpening_instance(sharpening_type)
# sharpened_image = sharpening_instance.sharpen(image)
# cv2.imshow('Sharpened Image', sharpened_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()