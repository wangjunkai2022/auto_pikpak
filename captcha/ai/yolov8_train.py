import os
from ultralytics import YOLO

if __name__ == "__main__":
    # # Load a model
    # model = YOLO('yolov8n-cls.yaml')  # build a new model from YAML
    # load a pretrained model (recommended for training)
    model = YOLO('yolov8n-cls.pt')
    # model = YOLO('yolov8n-cls.yaml').load('yolov8n-cls.pt')  # build from YAML and transfer weights

    # # Train the model
    root_path = os.path.abspath(os.path.dirname(__file__))
    train_path = os.path.join(root_path, "dataTrain")
    resume_path = os.path.join(root_path, "best.pt")
    results = model.train(data=train_path, imgsz=(
        608, 608), resume=resume_path)
    # print(results)
