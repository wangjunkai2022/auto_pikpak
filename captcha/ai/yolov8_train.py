from ultralytics import YOLO

if __name__ == "__main__":
    # # Load a model
    # model = YOLO('yolov8n-cls.yaml')  # build a new model from YAML
    model = YOLO('yolov8n-cls.pt')  # load a pretrained model (recommended for training)
    # model = YOLO('yolov8n-cls.yaml').load('yolov8n-cls.pt')  # build from YAML and transfer weights

    # # Train the model
    results = model.train(data='./dataTrain', imgsz=(600, 300),resume="./runs/classify/train/weights/best.pt")
    # print(results)
