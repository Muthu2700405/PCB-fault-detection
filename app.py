import os
import uuid
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from PIL import Image
import numpy as np

# ------------ CONFIG ------------
# model path (your best.pt in project root)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "best.pt")

UPLOAD_FOLDER = os.path.join("static", "uploads")
RESULT_FOLDER = os.path.join("static", "results")
ALLOWED_EXT = {"jpg", "jpeg", "png", "bmp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load YOLOv8 model (Ultralytics)
print("Loading model from:", MODEL_PATH)
model = YOLO(MODEL_PATH)  # loads model (may take a few seconds)

app = Flask(__name__, static_folder="static", template_folder="templates")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


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

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Save uploaded file with unique name
    orig_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{orig_name}"
    upload_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(upload_path)

    # Run prediction: returns Results
    # you can tune imgsz and conf (confidence threshold)
    results = model.predict(source=upload_path, imgsz=640, conf=0.25, save=False)

    # Single-image case: take first result
    res = results[0]

    # Extract detections
    boxes = res.boxes  # Boxes object
    num_detections = len(boxes)
    detected = []
    for b in boxes:
        # convert tensors to python values safely
        try:
            cls_id = int(b.cls.cpu().numpy()[0])
            conf = float(b.conf.cpu().numpy()[0])
            xyxy = b.xyxy.cpu().numpy()[0].tolist()
        except Exception:
            cls_id = int(b.cls)
            conf = float(b.conf)
            xyxy = [float(x) for x in b.xyxy[0]]

        name = model.names.get(cls_id, str(cls_id))
        detected.append({
            "class_id": cls_id,
            "name": name,
            "confidence": round(conf, 3),
            "xyxy": [round(v, 2) for v in xyxy]
        })

    # Create annotated image (res.plot returns an ndarray RGB)
    annotated_arr = res.plot()  # H,W,3 (RGB)
    annotated_pil = Image.fromarray(annotated_arr)

    # Save annotated image into static/results with same unique base name
    result_filename = unique_name  # same name as upload (makes mapping easy)
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    annotated_pil.save(result_path)

    # Return result URL (static route) and detection info
    result_url = url_for("static", filename=f"results/{result_filename}")
    return jsonify({
        "result_url": result_url,
        "detections": num_detections,
        "detected": detected
    })


if __name__ == "__main__":
    # debug=True for development only
    app.run(host="0.0.0.0", port=5000, debug=True)
