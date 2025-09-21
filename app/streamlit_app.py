import streamlit as st
import os
import sys
import cv2
from PIL import Image

# Adjust Python path to include src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import run_pipeline
from src.detection.pii_detection_pipeline import detect_and_link_pii

st.title("MirrorMask - Smarter PII Redaction")

# Simulate multi-user with session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = os.urandom(16).hex()
st.write(f"User Session: {st.session_state.user_id[:8]}...")

# File upload
uploaded_file = st.file_uploader("Upload Document", type=['png', 'jpg'])
if uploaded_file:
    input_path = f"temp/{uploaded_file.name}"
    os.makedirs("temp", exist_ok=True)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Preview detected PII
    detections, _, _, _ = detect_and_link_pii(input_path)
    img_cv = cv2.imread(input_path)
    for det in detections:
        x1, y1, x2, y2 = det['abs_bbox']
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green boxes
        cv2.putText(img_cv, det['type'], (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    preview_path = f"temp/preview_{uploaded_file.name}"
    cv2.imwrite(preview_path, img_cv)
    st.subheader("Detected PII")
    st.image(preview_path)
    
    # Redaction mode
    mode = st.selectbox("Redaction Mode", ["Standard", "Legal"])
    
    if st.button("Redact"):
        output_path = f"output/redacted_{uploaded_file.name}"
        redacted_path, audit = run_pipeline(input_path, output_path, doc_id=uploaded_file.name, mode=mode)
        
        # Side-by-side display
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(input_path)
        with col2:
            st.subheader("Redacted")
            st.image(redacted_path)
        
        # Download button
        with open(redacted_path, "rb") as f:
            st.download_button("Download Redacted", data=f, file_name=f"redacted_{uploaded_file.name}")
        
        # Show audit
        st.subheader("Audit Log")
        st.json(audit)
    
    if st.button("Clear"):
        st.session_state.clear()