import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import spacy
from ultralytics import YOLO
import os
from pytesseract import Output
from faker import Faker
from scipy.spatial.distance import euclidean

fake = Faker()
nlp = spacy.load("en_core_web_sm")  # Use sm for speed in prototype

def is_aadhaar(text):
    text = text.replace(" ", "")
    return text.isdigit() and len(text) == 12

def detect_pii(text):
    doc = nlp(text)
    pii = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE"]:
            pii.append((ent.text, "NAME" if ent.label_ == "PERSON" else "ADDRESS"))
        elif ent.label_ == "DATE":
            pii.append((ent.text, "DATE"))
    # Phone custom
    digits = ''.join(c for c in text if c.isdigit())
    if len(digits) == 10:
        pii.append((text, "PHONE"))
    # Aadhaar
    if is_aadhaar(text):
        pii.append((text, "AADHAAR"))
    return pii

def generate_dummy(pii_type):
    if pii_type == "NAME":
        return fake.name()
    elif pii_type == "ADDRESS":
        return fake.address().replace('\n', ', ')
    elif pii_type == "PHONE":
        return fake.numerify('##########')
    elif pii_type == "DATE":
        return fake.date(pattern='%d-%m-%Y')
    elif pii_type == "AADHAAR":
        return fake.numerify('#### #### ####')
    return "[Redacted]"

def preprocess_region(region):
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=10)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

def detect_and_link_pii(image_path, model_path="runs/detect/signverod_finetune4/weights/best.pt"):  # Use your latest model
    try:
        model = YOLO(model_path)
    except:
        model = YOLO("yolov8n.pt")
    
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found")
    
    height, width = img.shape[:2]
    
    # YOLO detections
    results = model.predict(image_path, conf=0.25, iou=0.45)  # Higher conf for prototype
    detections = []
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        names = result.names
        for box, cls, conf in zip(boxes, classes, confs):
            x1, y1, x2, y2 = map(int, box)
            class_name = names[int(cls)]
            region = img[y1:y2, x1:x2]
            preprocessed = preprocess_region(region)
            text = pytesseract.image_to_string(Image.fromarray(preprocessed), config='--psm 6').strip()
            pii_list = detect_pii(text)
            det = {
                "type": class_name,
                "bbox": [x1/width, y1/height, (x2-x1)/width, (y2-y1)/height],  # Normalized for YOLO-style
                "abs_bbox": [x1, y1, x2, y2],
                "confidence": float(conf),
                "text": text,
                "pii": pii_list
            }
            detections.append(det)
    
    # Full-image OCR for missed text PII
    preprocessed_img = preprocess_region(img)
    ocr_data = pytesseract.image_to_data(Image.fromarray(preprocessed_img), output_type=Output.DICT)
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i].strip()
        if text:
            pii_list = detect_pii(text)
            if pii_list:
                x1, y1, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                det = {
                    "type": "text",
                    "bbox": [x1/width, y1/height, w/width, h/height],
                    "abs_bbox": [x1, y1, x1+w, y1+h],
                    "confidence": 0.8,  # Arbitrary
                    "text": text,
                    "pii": pii_list
                }
                detections.append(det)
    
    # Link PII (heuristic: distance < 200px or same y)
    links = {}
    for i, det1 in enumerate(detections):
        center1 = ((det1['abs_bbox'][0] + det1['abs_bbox'][2])/2, (det1['abs_bbox'][1] + det1['abs_bbox'][3])/2)
        for j, det2 in enumerate(detections):
            if i != j and det1['type'] in ['signature', 'initials', 'photo'] and det2['type'] in ['text', 'name', 'phone', 'aadhaar', 'date']:
                center2 = ((det2['abs_bbox'][0] + det2['abs_bbox'][2])/2, (det2['abs_bbox'][1] + det2['abs_bbox'][3])/2)
                dist = euclidean(center1, center2)
                if dist < 200 or abs(center1[1] - center2[1]) < 50:  # Vertical align
                    links.setdefault(i, []).append(j)
                    links.setdefault(j, []).append(i)
    
    # Generate dummies for text PII
    dummies = {}
    for idx, det in enumerate(detections):
        if det['type'] in ['phone', 'date', 'aadhaar', 'text'] and det['pii']:
            pii_type = det['pii'][0][1]  # First PII type
            dummy = generate_dummy(pii_type)
            dummies[idx] = dummy
    
    return detections, links, dummies, img  # Return img for pipeline