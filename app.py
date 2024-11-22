from flask import Flask, render_template, request, send_file
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image = cv2.imread(file_path)

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
                perspective_points = np.float32([
                    [0, 0],
                    [image.shape[1] - 50, 50],
                    [50, image.shape[0] - 50],
                    [image.shape[1] - 50, image.shape[0] - 50]
                ])
                transformed_image = project_image(image, perspective_points)
            elif transform_type == 'translate':
                tx = int(request.form.get('tx', 50))  
                ty = int(request.form.get('ty', 50))  
                transformed_image = translate_image(image, tx, ty)

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.jpg')
            cv2.imwrite(output_path, transformed_image)
            return send_file(output_path, mimetype='image/jpeg')
    return render_template('index.html')

                
    
if __name__ == "__main__":
    app.run(debug=True)