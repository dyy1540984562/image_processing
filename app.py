import io
import cv2
import numpy as np
from flask import Flask, render_template, request, send_from_directory, send_file
import os
import logging
from ratelimit import limits, sleep_and_retry

from logic.sharpen_operator import ImageSharpeningFactory

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
    app.logger.info("upload start")
    file = request.files['file']
    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        app.logger.info("upload success")
        return 'Image upload successfully!', 200
    app.logger.info("upload failed")
    return 'Invalid file format.', 200

@app.route('/download', methods=['POST'])
@sleep_and_retry
@limits(calls=10, period=1)  # 每秒最多调用10次
def download():
    try:
        app.logger.info("download start")
        filename = request.form['filename']
        if allowed_file(filename):
            app.logger.info("download success")
            sharpened_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            return send_file(sharpened_path, mimetype='image/jpeg')
        else:
            return 'Invalid file format.', 200
    except BaseException as e:
        app.logger.error(e)
        return str(e), 200


@app.route('/sharpen', methods=['POST'])
@sleep_and_retry
@limits(calls=2, period=1)  # 每秒最多调用两次
def sharpen():
    try:
        app.logger.info("sharpen start")
        filename = request.json['filename']
        sharpenFactor = request.json['param']
        sharpening_type = request.json['type'] # 可以更改为'unsharp'或'scharr'
    except BaseException as e:
        app.logger.error(e)
        return str(e), 200
    if allowed_file(filename):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = cv2.imread(image_path)

        # Apply sharpening filter on the image
        sharpening_instance = ImageSharpeningFactory.create_sharpening_instance(sharpening_type)
        sharpened = sharpening_instance.sharpen(image, sharpenFactor)
        
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
        app.logger.info("binarize start")
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