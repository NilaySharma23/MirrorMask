import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import FileResponse
from src.pipeline import run_pipeline
import shutil

app = FastAPI(title="MirrorMask API")

API_KEYS = {
    "demo_key_1": "user1",
    "demo_key_2": "user2"
}

@app.post("/redact")
async def redact(file: UploadFile = File(...), api_key: str = Header(None), mode: str = "Standard"):
    print(f"Received API key: {api_key}")  # Debug print
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if mode not in ["Standard", "Legal"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'Standard' or 'Legal'.")
    
    input_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    output_path = f"output/redacted_{file.filename}"
    redacted_path, audit = run_pipeline(input_path, output_path, doc_id=file.filename, mode=mode)
    
    audit["user"] = API_KEYS[api_key]
    return {"redacted_path": redacted_path, "audit": audit, "file": FileResponse(redacted_path)}