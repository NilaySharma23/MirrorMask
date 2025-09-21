from ultralytics import YOLO
import os

if __name__ == '__main__':
    model = YOLO('yolov8n.pt')  # Load latest pretrained
    data_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
    results = model.train(data=data_path, epochs=50, imgsz=640, batch=8, device='0', name='signverod_finetune', project='runs/detect')