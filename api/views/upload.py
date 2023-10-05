import os

from flask import Blueprint, request, jsonify, flash, redirect
from werkzeug.utils import secure_filename
from transliterate import translit

file_upload_bp = Blueprint("file_upload", __name__)

# Конфигурация загрузки файлов
# photos = UploadSet("photos", IMAGES)
# configure_uploads(file_upload_bp, photos)
UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# Проверка на формат из ALLOWED_EXTENSIONS
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
        print(f'file - {file.filename}')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Транслитерация текста
            transliterate_file_name = translit(file.filename, 'ru', reversed=True)
            filename = secure_filename(transliterate_file_name)
            print(f'filename - {filename}')
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            print('OK')
        return 'OK'
