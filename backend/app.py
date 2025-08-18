import io
import base64
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
from ultralytics import YOLO

# --- CORRECTED LINE ---
# Added static_url_path='' to serve files like style.css from the root URL
app = Flask(__name__, static_folder='../frontend', static_url_path='')

try:
    model = YOLO('best.pt')
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/detect', methods=['POST'])
def detect():
    if not model:
        return jsonify({'error': 'Model could not be loaded.'}), 500
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))

            results = model(img)

            res_plotted = results[0].plot()
            
            result_img = Image.fromarray(res_plotted)

            buffered = io.BytesIO()
            result_img.save(buffered, format="JPEG")

            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            detected_classes = [model.names[int(c)] for c in results[0].boxes.cls]

            return jsonify({
                'image': 'data:image/jpeg;base64,' + img_str,
                'detections': detected_classes
            })

        except Exception as e:
            return jsonify({'error': f'An error occurred during detection: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)