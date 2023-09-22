import os

from flask import Blueprint, request, jsonify, flash, redirect
from werkzeug.utils import secure_filename

file_upload_bp = Blueprint("file_upload", __name__)

# Конфигурация загрузки файлов
# photos = UploadSet("photos", IMAGES)
# configure_uploads(file_upload_bp, photos)
UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@file_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(f'file - {file}')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(f'filename - {filename}')
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            print('OK')
        return 'OK'
