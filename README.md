# MirrorMask - Smarter Redaction for Visual PII

A hackathon prototype for context-aware PII redaction in documents. Detects and links PII (e.g., signatures, names, IDs) using YOLOv8 and spaCy, then redacts by replacing with dummy data (per hackathon guidelines). Preserves document usability for legal/healthcare/finance use. Audit logs stored in MongoDB for compliance.

## Features (Current Progress)
- Synthetic data generation with overlaps, edge cases, and PDF support.
- Fine-tuned YOLOv8 on SignverOD + synthetics for visual PII (signatures, photos).
- Text PII detection via easyOCR + spaCy/regex (names, Aadhaar, PAN, phone).
- Heuristic-based PII linking (e.g., signature to nearby name).
- Basic Streamlit UI for image upload and redaction preview (currently inpaints; dummy replacement in progress).
- MongoDB integration for audit storage (tested but not yet in pipeline).

Future: Dummy PII replacement, redaction modes (Standard/Legal/Anonymization), PDF/multi-page support, API/CLI, multi-user login, QR verification.

## Setup Instructions
This project uses large datasets and personal photos ignored in `.gitignore`. You'll need to recreate the `datasets/` folder and provide photo assets locally. Follow these steps to set up and run.

### 1. Clone and Install Dependencies
- Clone the repo: `git clone <your-repo-url>`
- Create a virtual environment (optional): `python -m venv venv` then `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows).
- Install dependencies: `pip install -r requirements.txt`
- Install Tesseract OCR: Download from [GitHub](https://github.com/tesseract-ocr/tesseract) and add to PATH.

### 2. Set Up MongoDB
- Sign up for MongoDB Atlas (free tier) at [mongodb.com](https://www.mongodb.com/cloud/atlas).
- Create a cluster, database ("mirrormask_db"), and collection ("audits").
- Copy your connection string (MONGODB_URI) to `.env` (use `.env.example` as template).
- Test connection: `python tests/test_db.py` (should insert/fetch a test document).

### 3. Prepare Datasets (Recreate `datasets/` Folder)
The `datasets/` folder is `.gitignore`’d due to size (>1GB). Recreate it as follows:
- Create the folder: `mkdir datasets`
- Download SignverOD from Kaggle: Go to [kaggle.com/datasets/victordibia/signverod](https://www.kaggle.com/datasets/victordibia/signverod), download the zip, extract to `datasets/signverod/` (should have `images/`, `tfrecords/`, CSV files).
- Convert to YOLO format: `python data/convert_signverod_to_yolo.py` (processes first 100 images/labels to `datasets/yolo_signverod/` for faster training).
- Prepare labels: `python data/prepare_yolo_labels.py` (cleans label formats and renames to match image filenames).
- (Optional) Label custom synthetics: Generate samples (Step 4), upload to Roboflow (free tier), annotate, export to `datasets/yolo_signverod/` (add to train/valid splits).
- Fine-tune YOLO: `python data/train_yolo.py` (uses `yolo_data.yaml`; outputs to `runs/detect/` and `models/yolov8_finetuned.pt`). Adjust epochs/augs as needed.

### 4. Prepare Assets
- The `assets/` folder contains `signature1.png`, `signature2.png`, `signature3.png` (included in repo).
- You must provide three face images named `photo1.png`, `photo2.png`, `photo3.png` in `assets/`. These are `.gitignore`’d due to privacy. Use public-domain or personal images (e.g., from [Unsplash](https://unsplash.com)) and rename them accordingly.

### 5. Generate Synthetic Data
- Run `python data/generate_synthetics.py` to create 5 sample PNGs (with PII) in `demo/inputs/`. One converts to PDF if `img2pdf` installed.

### 6. Run the App
- Start Streamlit: `streamlit run src/app.py`
- Upload a PNG/JPG from `demo/inputs/`, view original vs. redacted (currently inpaints; dummy replacement in progress).

### 7. (Future) Run API/CLI
- API: `uvicorn src/api:app --reload` (not implemented yet).
- CLI: Run with args (not implemented yet).

## Usage Demo
1. Upload image → Detects PII → Generates masks → Inpaints (preview side-by-side).
2. Clear uploads button resets.
For full flow: Upload → Detect/Link → Replace with dummies → Audit to DB → Download.

## Ethics and Compliance
- No real PII stored; only dummies and anonymized audits in MongoDB.
- Aligns with hackathon: Dummy replacement (no blur/mask), NoSQL DB, no LLMs, up-to-date models via fine-tuning on SignverOD.
- Multi-user/API planned for pluggability.

## Risks and Limitations
- Detection accuracy: YOLO ~70% mAP50 on signatures (low recall on samples); spaCy detects IDs (~66% conf) but may miss names.
- Linking: ~70% for close pairs; heuristic-based (future GNN).
- OCR fails on poor scans (console warnings).
- Current redaction: Inpainting (hackathon forbids blur/mask; switching to dummies).
- Time: <10s/page on CPU (tested).
- Edge cases: Complex layouts, multi-page PDFs (support coming).
