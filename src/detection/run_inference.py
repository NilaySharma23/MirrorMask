from ultralytics import YOLO
import json

def run_inference(model_path="runs/detect/signverod_finetune4/weights/best.pt", data_yaml="src/detection/data.yaml"):
    # Load model
    try:
        model = YOLO(model_path)
    except FileNotFoundError:
        print(f"Model {model_path} not found, falling back to yolov8n.pt")
        model = YOLO("yolov8n.pt")
    
    # Run validation with true metrics
    results = model.val(data=data_yaml, conf=0.1, iou=0.45, verbose=True)
    
    # Extract metrics
    metrics = {
        "precision": float(results.box.mp),  # Mean Precision across all classes
        "recall": float(results.box.mr),     # Mean Recall across all classes
        "mAP_0.5": float(results.box.map50), # mAP at IoU=0.5 across all classes
        "mAP_0.5:0.95": float(results.box.map),  # mAP at IoU=0.5:0.95 across all classes
        "per_class": {
            "signature": {
                "precision": float(results.box.p[0]) if len(results.box.p) > 0 else 0.0,
                "recall": float(results.box.r[0]) if len(results.box.r) > 0 else 0.0,
                "mAP_0.5": float(results.box.ap50[0]) if len(results.box.ap50) > 0 else 0.0
            },
            "initials": {
                "precision": float(results.box.p[1]) if len(results.box.p) > 1 else 0.0,
                "recall": float(results.box.r[1]) if len(results.box.r) > 1 else 0.0,
                "mAP_0.5": float(results.box.ap50[1]) if len(results.box.ap50) > 1 else 0.0
            },
            "phone": {
                "precision": float(results.box.p[2]) if len(results.box.p) > 2 else 0.0,
                "recall": float(results.box.r[2]) if len(results.box.r) > 2 else 0.0,
                "mAP_0.5": float(results.box.ap50[2]) if len(results.box.ap50) > 2 else 0.0
            },
            "date": {
                "precision": float(results.box.p[3]) if len(results.box.p) > 3 else 0.0,
                "recall": float(results.box.r[3]) if len(results.box.r) > 3 else 0.0,
                "mAP_0.5": float(results.box.ap50[3]) if len(results.box.ap50) > 3 else 0.0
            },
            "aadhar": {
                "precision": float(results.box.p[4]) if len(results.box.p) > 4 else 0.0,
                "recall": float(results.box.r[4]) if len(results.box.r) > 4 else 0.0,
                "mAP_0.5": float(results.box.ap50[4]) if len(results.box.ap50) > 4 else 0.0
            },
            "photo": {
                "precision": float(results.box.p[5]) if len(results.box.p) > 5 else 0.0,
                "recall": float(results.box.r[5]) if len(results.box.r) > 5 else 0.0,
                "mAP_0.5": float(results.box.ap50[5]) if len(results.box.ap50) > 5 else 0.0
            }
        }
    }
    
    # Save metrics to file
    with open("inference_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
    
    print("True validation metrics saved to inference_metrics.json")
    return metrics

if __name__ == "__main__":
    run_inference()