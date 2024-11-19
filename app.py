from flask import Flask, render_template, request, send_file
import cv2
import os
import numpy as np
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'static/output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Pastikan folder upload ada
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Pastikan folder output ada

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def reflect_image(image, axis):
    if axis == 'horizontal':
        reflected = cv2.flip(image, 1)
    elif axis == 'vertical':
        reflected = cv2.flip(image, 0)
    return reflected

# Fungsi untuk dilatasi (penskalaan)
def dilate_image(image, scale_x, scale_y):
    height, width = image.shape[:2]
    dilated = cv2.resize(image, (int(width * scale_x), int(height * scale_y)))
    return dilated

# Fungsi untuk rotasi (perputaran)
def rotate_image(image, angle):
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
    return rotated

# Fungsi untuk proyeksi perspektif
def project_image(image, perspective_points):
    height, width = image.shape[:2]
    original_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(original_points, perspective_points)
    projected = cv2.warpPerspective(image, matrix, (width, height))
    return projected

# Rute utama untuk halaman depan
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Mengambil file gambar yang diunggah
        file = request.files['image']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)

            # Mendapatkan parameter transformasi dari form HTML
            transform_type = request.form.get('transform')
            if transform_type == 'reflect_horizontal':
                transformed_image = reflect_image(image, 'horizontal')
            elif transform_type == 'reflect_vertical':
                transformed_image = reflect_image(image, 'vertical')
            elif transform_type == 'rotate':
                angle = float(request.form.get('angle', 45))
                transformed_image = rotate_image(image, angle)
            elif transform_type == 'dilate':
                scale_x = float(request.form.get('scale_x', 1.5))
                scale_y = float(request.form.get('scale_y', 1.5))
                transformed_image = dilate_image(image, scale_x, scale_y)
            elif transform_type == 'project':
                # Titik untuk proyeksi bisa diambil dari input user (atau gunakan default)
                perspective_points = np.float32([
                    [0, 0],
                    [image.shape[1] - 50, 50],
                    [50, image.shape[0] - 50],
                    [image.shape[1] - 50, image.shape[0] - 50]
                ])
                transformed_image = project_image(image, perspective_points)

            # Simpan gambar hasil transformasi
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.jpg')
            cv2.imwrite(output_path, transformed_image)
            return send_file(output_path, mimetype='image/jpeg')
    return render_template('index.html')


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if request.method == 'POST' :
        file = request.files['image']
        if file : 
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)
            
            transform_type = request.form.get('transform')
            if transform_type == 'dilate':
                scale_x = float(request.form.get('scale_x', 1.5))
                scale_y = float(request.form.get('scale_y', 1.5))
                transformed_image = dilate_image(image, scale_x, scale_y)
            
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.jpg')
            cv2.imwrite(output_path, transformed_image)
            return send_file(output_path, mimetype='image/jpeg')
    return render_template("index.html")
                
    
if __name__ == "__main__":
    app.run(debug=True)