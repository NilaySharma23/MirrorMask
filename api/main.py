from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from src.pipeline import run_pipeline
import os
import shutil

app = FastAPI(title="MirrorMask API")

# Simple API key auth for multi-user simulation
API_KEYS = {
    "demo_key_1": "user1",
    "demo_key_2": "user2"  # Add more for demo
}

@app.post("/redact")
async def redact(file: UploadFile = File(...), api_key: str = Header(None), mode: str = "Standard"):
    """
    Redact PII from an uploaded image.
    Args:
        file: Uploaded image (PNG/JPG).
        api_key: API key for authentication.
        mode: Redaction mode ("Standard" or "Legal").
    Returns:
        Dict with redacted image path and audit log.
    """
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if mode not in ["Standard", "Legal"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'Standard' or 'Legal'.")
    
    # Save uploaded file
    input_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Run pipeline
    output_path = f"output/redacted_{file.filename}"
    redacted_path, audit = run_pipeline(input_path, output_path, doc_id=file.filename, mode=mode)
    
    # Add user to audit
    audit["user"] = API_KEYS[api_key]
    
    return {"redacted_path": redacted_path, "audit": audit}