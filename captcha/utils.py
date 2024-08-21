import os
from urllib.parse import parse_qs, urlparse, urlunparse

import cv2
import numpy as np


def extract_parameters(url):
    # 解析 URL
    parsed_url = urlparse(url)

    # 提取查询参数并转换为字典
    params = parse_qs(parsed_url.query)

    # 将参数的值从列表转换为单一值
    params_dict = {key: value[0] for key, value in params.items()}

    return params_dict


def remove_parameters(url):
    # 解析 URL
    parsed_url = urlparse(url)

    # 创建一个新的 URL，不包含查询参数
    new_url = urlunparse(parsed_url._replace(query=''))

    return new_url


def domain_get(url):
    # 使用 urlparse 解析 URL
    parsed_url = urlparse(url)

    # 获取域名
    domain = parsed_url.netloc
    return domain

# 删除图片


def delete_img(img_path):
    dir_path = os.path.dirname(img_path)
    for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))
    print('删除缓存图片成功')


# 保存网络requests图片到指定位置
def save_requests_img(content, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "wb")as file:
        file.write(content)

# 重组切割图片


def image_run(img_path, frames):
    iamge, height, width = read_img(img_path)
    img_list = cut_img(iamge, height, width, frames[0]['matrix'])
    for i in range(len(frames)):
        matrix = frames[i]['matrix']
        temp_img = re_img(img_list, height, width, matrix)
        save_img(temp_img, os.path.join(
            os.path.abspath(
                os.path.dirname(img_path)
            ), str(i) + ".png"
        )
        )


# 保存图像
def save_img(img, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    cv2.imwrite(path, img)


# 导入原始图像
def read_img(path):
    img = cv2.imread(path)
    # 获取图像基本信息
    height, width, channel = img.shape
    return img, height, width


# 图像切割
def cut_img(img, height, width, matrix):
    # 切割图像
    img_list = [[0 for _ in range(len(matrix[0]))]
                for _ in range(len(matrix[0]))]
    for i in range(len(matrix[0])):
        for j in range(len(matrix[0])):
            # 纵向切割
            img_list[j][i] = img[i * height // len(matrix[0]): (i + 1) * height // len(matrix[0]),
                                 j * width // len(matrix[0]): (j + 1) * width // len(matrix[0])]
    return img_list


# 图像重组
def re_img(img_list, height, width, matrix):
    new_img_list = [[0 for _ in range(len(matrix[0]))]
                    for _ in range(len(matrix[0]))]
    for i in range(len(matrix[0])):
        for j in range(len(matrix[0])):
            k, l = matrix[i][j].split(',')
            new_img_list[i][j] = img_list[int(k)][int(l)]
    # 图像拼接
    img = np.zeros((height, width, 3), np.uint8)
    for i in range(len(matrix[0])):
        for j in range(len(matrix[0])):
            img[i * height // len(matrix[0]): (i + 1) * height // len(matrix[0]),
                j * width // len(matrix[0]): (j + 1) * width // len(matrix[0])] = new_img_list[i][j]
    return img
