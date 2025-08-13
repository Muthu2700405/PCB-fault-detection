# app.py
import os
import io
import uuid
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from PIL import Image

# ---------- CONFIG ----------
MODEL_PATH = "best.pt"   # place your YOLOv8 best.pt here
ALLOWED_EXT = {"jpg", "jpeg", "png", "bmp"}
UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins (Netlify/others)

# Load model (will take a few seconds)
print("Loading YOLOv8 model from:", MODEL_PATH)
model = YOLO(MODEL_PATH)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "PCB YOLO backend running"})


@app.route("/detect", methods=["POST"])
def detect():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Save file with unique name
    orig = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{orig}"
    upload_path = os.path.join(UPLOAD_DIR, unique_name)
    file.save(upload_path)

    # Run prediction (single image)
    results = model.predict(source=upload_path, imgsz=640, conf=0.25, save=False)
    res = results[0]

    # Gather detections
    boxes = res.boxes  # Boxes object
    detected = []
    for b in boxes:
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

    # Build annotated image (res.plot returns RGB numpy array)
    annotated_np = res.plot()  # H,W,3 RGB ndarray
    annotated_pil = Image.fromarray(annotated_np)

    # Save annotated image to results folder
    result_path = os.path.join(RESULT_DIR, unique_name)
    annotated_pil.save(result_path)

    # Encode annotated image to base64 for easy transfer
    buf = io.BytesIO()
    annotated_pil.save(buf, format="JPEG")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({
        "image_b64": img_b64,
        "detections": len(detected),
        "detected": detected
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
