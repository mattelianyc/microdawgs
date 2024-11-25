# /fine_tune_service/app.py
from fine_tune_sd import fine_tune_model
from flask import Flask, request, jsonify, send_file
import os
from io import BytesIO
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from diffusers import StableDiffusionPipeline

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "Fine-tuning Text-to-Image AI Model Microservice"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        return jsonify({'message': 'File uploaded successfully', 'filepath': filepath}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/fine_tune', methods=['POST'])
def fine_tune():
    image_dir = "images"  # Assuming the images are in the "images" directory
    if not os.path.exists(image_dir) or not os.listdir(image_dir):
        return jsonify({'error': 'No images found in the specified directory'}), 400

    result = fine_tune_model(image_dir)
    return jsonify({'message': result}), 200

@app.route('/inference', methods=['POST'])
def inference():
    if 'text' not in request.form:
        return jsonify({'error': 'No text provided'}), 400

    text = request.form['text']
    inputs = CLIPProcessor(text=text, return_tensors="pt").to("cuda")
    image = model(**inputs).images[0]

    output_path = os.path.join(UPLOAD_FOLDER, 'generated_image.png')
    image.save(output_path)

    return send_file(output_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
