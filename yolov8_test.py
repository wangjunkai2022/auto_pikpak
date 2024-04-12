from ultralytics import YOLO
import numpy as mp

if __name__ == "__main__":
    # # Load a model
    # model = YOLO('yolov8n-cls.yaml')  # build a new model from YAML
    model = YOLO('./runs/classify/train4/weights/best.pt')  # load a pretrained model (recommended for training)
    # model = YOLO('yolov8n-cls.yaml').load('yolov8n-cls.pt')  # build from YAML and transfer weights

    # # Train the model
    # results = model.train(data='/Users/evan/codes/Other/auto_pikpak/dataTrain', epochs=109, imgsz=64)
    # print(results)
    results = model(source='./images/1001.png')
    # mp.argmax(results[0].probs.data.tolist())
    names = results[0].names
    probs = results[0].probs.data.tolist()
    id = names[mp.argmax(probs)]
    print(names)
    print(probs)
    print(id)
    # print(results)
