from flask import Flask, render_template, request, send_file, make_response, jsonify
import cv2
import os
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'static/output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def translate_image(image, tx, ty):
    height, width = image.shape[:2]
    translation_matrix = np.float32([[1, 0, tx], [0, 1, ty]])
    translated = cv2.warpAffine(image, translation_matrix, (width, height))
    return translated

def reflect_image(image, axis):
    if axis == 'horizontal':
        reflected = cv2.flip(image, 1)
    elif axis == 'vertical':
        reflected = cv2.flip(image, 0)
    return reflected

def dilate_image(image, scale_x, scale_y):
    height, width = image.shape[:2]
    dilated = cv2.resize(image, (int(width * scale_x), int(height * scale_y)))
    return dilated

def rotate_image(image, angle):
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
    return rotated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dilate', methods=['GET', 'POST'])
def dilate():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)

            scale = float(request.form.get('scale', 2))

            dilated_image = dilate_image(image, scale, scale)

            _, img_data_original = cv2.imencode('.jpg', image)
            _, img_data_dilated = cv2.imencode('.jpg', dilated_image)

            response = {
                'original': img_data_original.tobytes().hex(),
                'transformed': img_data_dilated.tobytes().hex()
            }
            return jsonify(response)

    return render_template('dilate.html')

@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)

            angle = float(request.form.get('angle', 45))
            
            transformed_image = rotate_image(image, angle)

            _, img_data_original = cv2.imencode('.jpg', image)
            _, img_data_transformed = cv2.imencode('.jpg', transformed_image)
        
            response = {
                'original': img_data_original.tobytes().hex(),
                'transformed': img_data_transformed.tobytes().hex()
            }
            return jsonify(response)
        
    return render_template('rotate.html')

@app.route('/reflect', methods=['GET', 'POST'])
def reflect():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)

            transform = request.form.get('transform', 'horizontal')
            if transform == 'horizontal':
                transformed_image = reflect_image(image, 'horizontal')
            elif transform == 'vertical':
                transformed_image = reflect_image(image, 'vertical')
            else:
                return jsonify({'error': 'Invalid transform type'}), 400

            _, img_data_original = cv2.imencode('.jpg', image)
            _, img_data_transformed = cv2.imencode('.jpg', transformed_image)

            response = {
                'original': img_data_original.tobytes().hex(),
                'transformed': img_data_transformed.tobytes().hex()
            }
            return jsonify(response)

    return render_template('index.html')

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)

            tx = int(request.form.get('tx', 0))
            ty = int(request.form.get('ty', 0))

            transformed_image = translate_image(image, tx, ty)

            _, img_data_original = cv2.imencode('.jpg', image)
            _, img_data_transformed = cv2.imencode('.jpg', transformed_image)

            response = {
                'original': img_data_original.tobytes().hex(),
                'transformed': img_data_transformed.tobytes().hex()
            }
            return jsonify(response)

    return render_template('translate.html')

if __name__ == "__main__":
    app.run(debug=True)