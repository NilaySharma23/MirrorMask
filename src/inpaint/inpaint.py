import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def create_mask(img_shape, detections):
    """
    Create a binary mask for inpainting based on detected PII bounding boxes.
    White (255) where PII needs to be inpainted, black (0) elsewhere.
    """
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    for det in detections:
        x1, y1, x2, y2 = det['abs_bbox']
        padding = 10  # Add padding to ensure full PII coverage
        x1, y1, x2, y2 = max(0, x1 - padding), max(0, y1 - padding), min(img_shape[1], x2 + padding), min(img_shape[0], y2 + padding)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)  # White for inpainting
    return mask

def inpaint_and_replace(image_path, detections, dummies, output_path, mode="Standard"):
    """
    Inpaint PII regions using OpenCV and overlay dummy text for text-based PII.
    Args:
        image_path: Path to input image.
        detections: List of PII detections from pii_detection_pipeline.
        dummies: Dict mapping detection indices to dummy text (e.g., fake names).
        output_path: Path to save redacted image.
        mode: "Standard" (use dummies) or "Legal" (use "[Redacted]").
    Returns:
        Path to the redacted image.
    """
    # Load image
    img_cv = cv2.imread(image_path)
    if img_cv is None:
        raise ValueError(f"Image not found: {image_path}")

    # Create mask for all PII regions
    mask = create_mask(img_cv.shape, detections)
    
    # Inpaint using OpenCV (TELEA algorithm for smooth document results)
    inpainted_cv = cv2.inpaint(img_cv, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # Convert to PIL for text overlay
    inpainted_pil = Image.fromarray(cv2.cvtColor(inpainted_cv, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(inpainted_pil)
    
    # Load font (use project's handwritten font for realism)
    font_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), 
                            'data', 'assets', 'IndieFlower-Regular.ttf')
    try:
        font = ImageFont.truetype(font_path, 20)  # Size 20 for document text
    except Exception as e:
        print(f"Font load failed: {e}. Using default font.")
        font = ImageFont.load_default()
    
    # Overlay dummy text for text-based PII
    for idx, det in enumerate(detections):
        if idx in dummies and det['type'] in ['phone', 'date', 'aadhaar', 'text']:
            x1, y1, _, _ = det['abs_bbox']
            overlay_text = dummies[idx] if mode == "Standard" else "[Redacted]"
            draw.text((x1, y1), overlay_text, fill=(0, 0, 0), font=font)
    
    # Save final image
    final_cv = cv2.cvtColor(np.array(inpainted_pil), cv2.COLOR_RGB2BGR)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, final_cv)
    return output_path