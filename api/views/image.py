from flask import Blueprint, send_file

# Создаем блюпринт
image_blueprint = Blueprint('image', __name__)

UPLOAD_FOLDER = './upload'


@image_blueprint.route('/image/<string:img>', methods=['GET'])
def get_image(img):
    # Путь к изображению на сервере
    image_path = UPLOAD_FOLDER + '/' + img

    # Отправить изображение как файл
    return send_file(image_path, mimetype='image/jpeg')
