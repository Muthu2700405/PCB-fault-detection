# flask_py_updated.py

import os
import uuid
import io  # Add this import
import base64  # Add this import
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from PIL import Image
import numpy as np

# --- CONFIG (remains the same) ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "best.pt")
model = YOLO(MODEL_PATH)
app = Flask(__name__, static_folder="static", template_folder="templates")

# You don't need these folders or the allowed_file function anymore
# if you process everything in memory.

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # 1. Read the image directly into memory
    try:
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        return jsonify({"error": f"Error reading image: {e}"}), 400

    # 2. Run prediction on the in-memory image
    results = model.predict(source=img, imgsz=640, conf=0.25, save=False)
    res = results[0]

    # --- Detection extraction logic (remains the same) ---
    boxes = res.boxes
    num_detections = len(boxes)
    detected = []
    # ... (your loop for processing boxes goes here, no changes needed)
    for b in boxes:
        try:
            cls_id = int(b.cls.cpu().numpy()[0])
            conf = float(b.conf.cpu().numpy()[0])
        except Exception:
            cls_id = int(b.cls)
            conf = float(b.conf)
        name = model.names.get(cls_id, str(cls_id))
        detected.append({"name": name, "confidence": round(conf, 3)})

    # 3. Get annotated image and convert to Base64
    annotated_arr = res.plot()
    annotated_pil = Image.fromarray(annotated_arr[..., ::-1]) # Convert BGR to RGB
    
    buffered = io.BytesIO()
    annotated_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 4. Return the Base64 string in the JSON
    return jsonify({
        "result_image_b64": img_str,  # Changed from result_url
        "detections": num_detections,
        "detected": detected
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)