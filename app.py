import io
import cv2
import numpy as np
from flask import Flask, render_template, request, send_from_directory, send_file
import os
import logging
from ratelimit import limits, sleep_and_retry

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = ['jpg', 'jpeg', 'png', 'gif']
app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
@sleep_and_retry
@limits(calls=2, period=1)  # 每秒最多调用两次
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@sleep_and_retry
@limits(calls=2, period=1)  # 每秒最多调用两次
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        app.logger.info("upload success")
        return 'Image upload successfully!', 200
    app.logger.info("upload failed")
    return 'Invalid file format.', 200

@app.route('/download')
@sleep_and_retry
@limits(calls=2, period=1)  # 每秒最多调用两次
def download():
    try:
        filename = '<filename>'  # Fill in the actual filename here
        app.logger.info("download success")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except BaseException as e:
        app.logger.error(e)
        return str(e), 200


@app.route('/sharpen', methods=['POST'])
@sleep_and_retry
@limits(calls=2, period=1)  # 每秒最多调用两次
def sharpen():
    try:
        filename = request.json['filename']
        sharpenFactor = request.json['param']
    except BaseException as e:
        app.logger.error(e)
        return str(e), 200
    if allowed_file(filename):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = cv2.imread(image_path)

        # Apply sharpening filter on the image
        sharpened = cv2.filter2D(image, -1, kernel=sharpenFactor * np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
        
        # Save the sharpened image
        sharpened_path = os.path.join(app.config['UPLOAD_FOLDER'], "sharpen_" + filename)
        cv2.imwrite(sharpened_path, sharpened)
        app.logger.info("sharpen success")
        return send_file(sharpened_path, mimetype='image/jpeg')
    app.logger.info("sharpen failed")
    return 'Invalid file format.', 200


@app.route('/binarize', methods=['POST'])
@sleep_and_retry
@limits(calls=2, period=1)  # 每秒最多调用两次
def binarize():
    try:
        filename = request.json['filename']
        threshold = request.json['param']
    except BaseException as e:
        app.logger.error(e)
        return str(e), 200
    if allowed_file(filename):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = cv2.imread(image_path, 0)  # Read the image in grayscale

        # Apply binary thresholding on the image
        _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)

        # Save the binarized image
        binary_path = os.path.join(app.config['UPLOAD_FOLDER'], "binary_" + filename)
        cv2.imwrite(binary_path, binary)
        app.logger.info("binarize success")
        return send_file(binary_path, mimetype='image/jpeg')
    app.logger.info("binarize failed")
    return 'Invalid file format.', 200


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5000)