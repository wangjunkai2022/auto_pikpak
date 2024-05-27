import base64
from io import BytesIO
import re
import time
from ultralytics import YOLO
import numpy as mp
from PIL import Image


def byte_to_image(byte_data, image_path=None):
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img


def ai_test_byte(byte):
    model = YOLO('./runs/classify/train/weights/best.pt')
    source = byte_to_image(byte)
    results = model(source)
    # mp.argmax(results[0].probs.data.tolist())
    names = results[0].names
    probs = results[0].probs.data.tolist()
    id = names[mp.argmax(probs)]
    print(names)
    print(probs)
    print(id)
    return id


if __name__ == "__main__":
    # # Load a model
    # model = YOLO('yolov8n-cls.yaml')  # build a new model from YAML
    # load a pretrained model (recommended for training)
    # model = YOLO('./runs/classify/train/weights/best.pt')
    # model = YOLO('yolov8n-cls.yaml').load('yolov8n-cls.pt')  # build from YAML and transfer weights

    # # Train the model
    # results = model.train(data='/Users/evan/codes/Other/auto_pikpak/dataTrain', epochs=109, imgsz=64)
    # print(results)
    image_path = "./images/0007_ok.png"
    # image = open(image_path, 'rb').read()results = model(Image.open(image)
    #                                                      )
    # # mp.argmax(results[0].probs.data.tolist())
    # names = results[0].names
    # probs = results[0].probs.data.tolist()
    # id = names[mp.argmax(probs)]
    # print(names)
    # print(probs)
    # print(id)
    # print(results)
    __time = time.time()
    with open(image_path, "rb") as imagefile:
        convert = imagefile.read()
    ai_test_byte(convert)
    print(time.time() - __time)
