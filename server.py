import datetime

from bson import ObjectId
from flask import Blueprint
from flask import Flask, make_response, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, jwt_required, get_jwt_identity

from api.views.cp.cp import api_cp
from api.views.edit_status import api_edit_status
from api.views.get_posts import api_get_posts
from api.views.get_tags import api_get_tags
from api.views.image import image_blueprint
from api.views.login import api_login
from api.views.logout import api_logout
from api.views.post_rating import api_post_rating
from api.views.get_user import api_get_user
from api.views.refresh import api_refresh
from api.views.subscribe import api_subscribe
from api.views.unsubscribe import api_unsubscribe
from api.views.get_subs_posts import api_get_subs_posts
from api.views.get_post_view import api_get_post_view
from api.views.get_post_comments import api_get_post_comments
from api.views.add_post import api_add_post
from api.views.add_comment import api_add_comment
from api.views.del_post import api_del_post
from api.views.edit_post import api_edit_post
from api.views.edit_comment import api_edit_comment
from api.views.del_comment import api_del_сomment
from api.views.get_users import api_get_users
from api.views.search import api_search
from api.views.registration import api_registration
from api.views.upload import file_upload_bp

# переменные из файла mongo.py
from mongo import users_collection, posts_collection

app = Flask(__name__)
app.secret_key = 'mysecretkey'
CORS(app, supports_credentials=True)
api = Blueprint('api', __name__)

# регистрируем blueprint
app.register_blueprint(api, url_prefix='/api')
# добавление поста
app.register_blueprint(api_add_post, url_prefix='/api')
# получение постов
app.register_blueprint(api_get_posts, url_prefix='/api')
# изменение рейтинга поста
app.register_blueprint(api_post_rating, url_prefix='/api')
# получение юзера
app.register_blueprint(api_get_user, url_prefix='/api')
# подписка на юзера
app.register_blueprint(api_subscribe, url_prefix='/api')
# отписка от юзера
app.register_blueprint(api_unsubscribe, url_prefix='/api')
# получение постов от авторов на которых подписан
app.register_blueprint(api_get_subs_posts, url_prefix='/api')
# получение поста для расшириного просмотра
app.register_blueprint(api_get_post_view, url_prefix='/api')
# получение комментариев для расшириного просмотра
app.register_blueprint(api_get_post_comments, url_prefix='/api')
# добавление комментария
app.register_blueprint(api_add_comment, url_prefix='/api')
# удаление поста
app.register_blueprint(api_del_post, url_prefix='/api')
# редактирование поста
app.register_blueprint(api_edit_post, url_prefix='/api')
# редактирование комментария
app.register_blueprint(api_edit_comment, url_prefix='/api')
# удаление комментария
app.register_blueprint(api_del_сomment, url_prefix='/api')
# получение юзеров
app.register_blueprint(api_get_users, url_prefix='/api')
# по
app.register_blueprint(api_search, url_prefix='/api')
# рефреш
app.register_blueprint(api_refresh, url_prefix='/api')
# регистрация
app.register_blueprint(api_registration, url_prefix='/api')
# Log in
app.register_blueprint(api_login, url_prefix='/api')
# Log out
app.register_blueprint(api_logout, url_prefix='/api')
# загрузка файлов
app.register_blueprint(file_upload_bp, url_prefix="/api")
# отдать файл
app.register_blueprint(image_blueprint, url_prefix="/api")
# отдать теги
app.register_blueprint(api_get_tags, url_prefix="/api")
# изменить текстовый статус пользователя
app.register_blueprint(api_edit_status, url_prefix="/api")
#
# CP
app.register_blueprint(api_cp, url_prefix="/api")

# задаем секретный ключ для подписи токена
app.config['JWT_SECRET_KEY'] = '23sa3501080X'
# Ожидаем токенs в куках и хедерах
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
# Имя куки, в которой ожидается refresh-токен
app.config['JWT_REFRESH_COOKIE_NAME'] = 'token'

jwt = JWTManager(app)  # инициализируем объект JWTManager


@app.after_request
def add_cors_headers(response):
    # response.headers['Access-Control-Allow-Origin'] = 'http://194.87.236.158:3000/'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    # response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-requested-with'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    app.run()
