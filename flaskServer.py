import datetime

from bson import ObjectId
from flask import Blueprint
from flask import Flask, make_response, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, jwt_required, get_jwt_identity
from api.views.get_posts import api_get_posts
from api.views.get_tags import api_get_tags
from api.views.image import image_blueprint
from api.views.login import api_login
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
# получение юзеров
app.register_blueprint(api_search, url_prefix='/api')
# рефреш
app.register_blueprint(api_refresh, url_prefix='/api')
# регистрация
app.register_blueprint(api_registration, url_prefix='/api')
# логин
app.register_blueprint(api_login, url_prefix='/api')
# загрузка файлов
app.register_blueprint(file_upload_bp, url_prefix="/api")
# отдать файл
app.register_blueprint(image_blueprint, url_prefix="/api")
# отдать теги
app.register_blueprint(api_get_tags, url_prefix="/api")

# задаем секретный ключ для подписи токена
app.config['JWT_SECRET_KEY'] = '23sa3501080X'
# Ожидаем токенs в куках и хедерах
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
# Имя куки, в которой ожидается refresh-токен
app.config['JWT_REFRESH_COOKIE_NAME'] = 'token'

jwt = JWTManager(app)  # инициализируем объект JWTManager


# обработка запроса на авторизацию пользователя
# @app.route('/api/login', methods=['POST'])
# def login():
#     # получаем данные из запроса
#     data = request.json
#     # ищем пользователя в базе данных
#     user = users_collection.find_one({'username': data['username']}, {'statusText': 0, 'rating': 0, 'refresh_token': 0})
#     if user is None:
#         print(f'Пользователя с логином {data["username"]} не существует')
#         return {'messageError': f'Пользователя с логином {data["username"]} не существует'}, 401
#     # проверяем пароль
#     if user['password'] == data['password']:
#         # создаем токен, вынести в отдельную функцию
#         access_token = create_access_token(
#             identity=str(user['_id']), expires_delta=datetime.timedelta(seconds=5))
#         refresh_token = create_refresh_token(
#             identity=str(user['_id']), expires_delta=datetime.timedelta(days=30))
#         # добавляем токен в бд
#         users_collection.update_one({'username': data['username']}, {
#             '$set': {'refresh_token': refresh_token}})
#         # после проверки пароля удаляю его из объекта юзера, перед ответом на клиент
#         del user['password']
#         user['subscribers'] = [str(u) for u in user['subscribers']]
#         # Objectid переводим в строку
#         user['_id'] = str(user['_id'])
#         # записываем айди из монго дб в переменную id
#         user['id'] = user['_id']
#         # тут использую make_response т.к. set_cookie метод объекта response без него получаю ошибку 'dict' object has no attribute 'set_cookie'
#         # в остальных ответах фласк сам преобразует в json
#         response = make_response({'user_obj': user, 'isAuth': True,
#                                   'access_token': access_token, 'refresh_token': refresh_token})
#         # response.set_cookie('refresh_token', refresh_token, httponly=True, max_age=30*24*60*60, samesite='None', secure=True, path='/api')
#         response.set_cookie('token', refresh_token, httponly=True, max_age=30 * 24 * 60 * 60,
#                             samesite='None', secure=True, path='/api')  # попробовать секьюр флаг поменять
#         return response
#     # возвращаем ошибку
#     print('Неверный пароль')
#     return {'messageError': 'Неверный пароль'}, 401


@app.route('/api/logout', methods=['GET'])
@jwt_required(refresh=True)
def logout():
    # получаем id юзера из токена 
    current_user = get_jwt_identity()
    # затираем токен в бд
    users_collection.update_one({'id': current_user}, {'$set': {'refresh_token': ''}})
    response = make_response({'message': 'User logged out successfully'})
    response.delete_cookie('token')
    response.set_cookie('token', '', httponly=True,
                        max_age=30 * 24 * 60 * 60, samesite='None', secure=True, path='/api')
    return response


@app.route('/api/user/<string:user_id>', methods=['POST', 'OPTIONS'])  # исправить передачу айди юзера
@jwt_required()  # использование декоратора для проверки токена
def upd_user(user_id):
    """Change Textststus"""

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    status_text = data['statusText']
    print(f'status_text - {status_text}')
    print(f'userId - {user_id}')
    users_collection.update_one(
        {'_id': ObjectId(user_id)}, {'$set': {'statusText': status_text}})
    response = {'statusText': status_text}
    return response


@app.after_request
def add_cors_headers(response):
    # response.headers['Access-Control-Allow-Origin'] = 'http://194.87.236.158:3000/'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-requested-with'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    app.run()
