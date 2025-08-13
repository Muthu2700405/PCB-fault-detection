from flask import Flask, request, jsonify
import torch
from PIL import Image
import io
import base64
import os

app = Flask(__name__)

# Load YOLO model
MODEL_PATH = "best.pt"
model = torch.hub.load('ultralytics/yolov8', 'custom', path=MODEL_PATH)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "PCB Detector API is running"})

@app.route("/detect", methods=["POST"])
def detect():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    img = Image.open(file.stream).convert("RGB")

    # Run YOLO
    results = model(img)
    detections = results.pandas().xyxy[0].to_dict(orient="records")

    # Save annotated image to memory
    img_bytes = io.BytesIO()
    results.save(save_dir="static")  # optional if you want file output
    results.render()  
    rendered_img = Image.fromarray(results.ims[0])
    rendered_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Encode image to Base64
    img_base64 = base64.b64encode(img_bytes.read()).decode("utf-8")

    # Prepare detection list
    detected_list = [
        {"name": d["name"], "confidence": round(float(d["confidence"]), 2)}
        for d in detections
    ]

    return jsonify({
        "detections": len(detected_list),
        "detected": detected_list,
        "result_image_b64": img_base64
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
