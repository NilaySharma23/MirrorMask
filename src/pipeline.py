import json
from datetime import datetime
import pymongo
from dotenv import load_dotenv
import os
from src.detection.pii_detection_pipeline import detect_and_link_pii
from src.inpaint.inpaint import inpaint_and_replace

# Initialize MongoDB
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in .env")
client = pymongo.MongoClient(MONGODB_URI)
db = client["mirrormask_db"]
audits_collection = db["audits"]

def run_pipeline(input_path, output_path, doc_id=None, mode="Standard"):
    """
    Run the full MirrorMask pipeline: detect PII, inpaint, replace with dummies, and log audit.
    Args:
        input_path: Path to input image.
        output_path: Path to save redacted image.
        doc_id: Unique identifier for the document (defaults to filename).
        mode: "Standard" (dummy replacement) or "Legal" ([Redacted] placeholder).
    Returns:
        Tuple of (redacted image path, audit log dict).
    """
    if not doc_id:
        doc_id = os.path.basename(input_path)
    
    # Step 1: Detect and link PII, generate dummies
    detections, links, dummies, _ = detect_and_link_pii(input_path)
    
    # Convert integer keys to strings for MongoDB
    dummies_str_keys = {str(k): v for k, v in dummies.items()}
    links_str_keys = {str(k): v for k, v in links.items()}
    
    # Step 2: Inpaint and replace with dummies
    redacted_path = inpaint_and_replace(input_path, detections, dummies, output_path, mode=mode)
    
    # Step 3: Create audit log (JSON-serializable)
    audit = {
        "doc_id": doc_id,
        "timestamp": datetime.now().isoformat(),
        "detections": [
            {
                "type": det["type"],
                "bbox": det["bbox"],
                "abs_bbox": det["abs_bbox"],
                "confidence": det["confidence"],
                "text": det["text"],
                "pii": det["pii"]
            } for det in detections
        ],  # Deep copy to avoid numpy types
        "links": links_str_keys,
        "dummies_used": dummies_str_keys,
        "redaction_mode": mode,
        "output_path": redacted_path
    }
    
    # Store in MongoDB
    try:
        audits_collection.insert_one(audit.copy())  # Use copy to avoid modifying original
        print(f"Audit inserted to MongoDB for {doc_id}")
    except Exception as e:
        print(f"MongoDB insert failed: {e}. Saving locally only.")
    
    # Save local JSON backup
    audit_dir = "audit"
    os.makedirs(audit_dir, exist_ok=True)
    audit_path = os.path.join(audit_dir, f"{doc_id}_audit.json")
    try:
        with open(audit_path, "w") as f:
            json.dump(audit, f, indent=4)
        print(f"Audit saved locally: {audit_path}")
    except Exception as e:
        print(f"Failed to save audit JSON: {e}")
    
    return redacted_path, audit