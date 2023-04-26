import datetime
import random

from flask import Blueprint
from flask import Flask, make_response, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from api import api
from api.views.get_posts import api_get_posts
from api.views.post_rating import api_post_rating

# переменные из файла mongo.py
from mongo import users_collection, posts_collection


app = Flask(__name__)
app.secret_key = 'mysecretkey'
CORS(app, supports_credentials=True)
api = Blueprint('api', __name__)

# регистрируем blueprint
app.register_blueprint(api, url_prefix='/api')
# получение постов
app.register_blueprint(api_get_posts, url_prefix='/api')
# изменение рейтинга поста
app.register_blueprint(api_post_rating, url_prefix='/api')


# задаем секретный ключ для подписи токена
app.config['JWT_SECRET_KEY'] = '23sa3501080X'
# Ожидаем токенs в куках и хедерах
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
# Имя куки, в которой ожидается refresh-токен
app.config['JWT_REFRESH_COOKIE_NAME'] = 'token'

jwt = JWTManager(app)  # инициализируем объект JWTManager


# обработка запроса на регистрацию пользователя !не доделана
@app.route('/api/register', methods=['POST'])
def register():
    # получаем данные из запроса
    data = request.json

    # проверяем, что такой пользователь не существует
    user = users_collection.find_one(
        {'username': data['username']}, {'_id': 0})
    if user:
        # существует
        return {'error': 'User already exists'}
    else:
        # создаем нового пользователя
        if data['username'] and data['password']:
            #  проверяем что логин и пароль передали
            print(users_collection.count_documents({}))
            length_users = users_collection.count_documents({})
            usr = {
                "id": length_users + 1,
                "username": data['username'],
                "password": data['password'],  # сделать хеширование
                "img": f"https://randomuser.me/api/portraits/men/{random.randint(1, 100)}.jpg",
                "rating": 100,
                "statusText": "newbie"
            }
            users_collection.insert_one(usr)
            return {'isReg': True}
        else:
            return {'isReg': False}


# обработка запроса на авторизацию пользователя
@app.route('/api/login', methods=['POST'])
def login():
    # получаем данные из запроса
    data = request.json
    # ищем пользователя в базе данных
    user = users_collection.find_one({'username': data['username']}, {
                                     '_id': 0, 'statusText': 0, 'rating': 0, 'refresh_token': 0})
    if user is None:
        print(f'Пользователя с логином {data["username"]} не существует')
        return {'messageError': f'Пользователя с логином {data["username"]} не существует'}, 401
    # проверяем пароль
    if user['password'] == data['password']:
        # создаем токен, вынести в отдельную функцию
        access_token = create_access_token(
            identity=user['id'], expires_delta=datetime.timedelta(seconds=5))
        refresh_token = create_refresh_token(
            identity=user['id'], expires_delta=datetime.timedelta(days=30))
        # добавляем токен в бд
        users_collection.update_one({'username': data['username']}, {
                                    '$set': {'refresh_token': refresh_token}})
        # после проверки пароля удаляю его из объекта юзера, перед ответом на клиент
        del user['password']
        # тут использую make_response т.к. set_cookie метод объекта response без него получаю ошибку 'dict' object has no attribute 'set_cookie'
        # в остальных ответах фласк сам преобразует в json
        response = make_response({'user_obj': user, 'isAuth': True,
                                 'access_token': access_token, 'refresh_token': refresh_token})
        # response.set_cookie('refresh_token', refresh_token, httponly=True, max_age=30*24*60*60, samesite='None', secure=True, path='/api')
        response.set_cookie('token', refresh_token, httponly=True, max_age=30*24*60*60,
                            samesite='None', secure=True, path='/api')  # попробовать секьюр флаг поменять
        return response
    # возвращаем ошибку
    print('Неверный пароль')
    return {'messageError': 'Неверный пароль'}, 401


# Эндпоинт для обновления access token по refresh token
@app.route('/api/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    # получаем рефреш токен из куки
    token = request.cookies.get('token')
    print(f"cookie  -  {request.cookies.get('token')}")

    # получаем id юзера из токена 
    current_user = get_jwt_identity()
    # print(f'user - {current_user}')

    # получаем данные юзера
    user = users_collection.find_one({'id': current_user}, {'_id': 0, 'password': 0, 'statusText': 0, 'rating': 0})
    print(f'user - {user["refresh_token"]}')
    
    # !!!! из-за 2х запросов подряд  к рефрешу токен не успевает обновится в куках и кука призодит со старым токеном а в бд уже новый
    # проверка токена с токеном из бд
    # if token != user['refresh_token']:
    #     return {'message': 'No valid token'}

    # после проверки токена удаляю его из объекта юзера, перед ответом на клиент
    del user['refresh_token']

    new_access_token = create_access_token(
        identity=current_user, expires_delta=datetime.timedelta(seconds=5))
    new_refresh_token = create_refresh_token(
        identity=current_user, expires_delta=datetime.timedelta(days=30))
    print('новые токены сгенерированы')

    # обновляем токен в бд
    users_collection.update_one({'id': current_user}, {'$set': {'refresh_token': new_refresh_token}})
    # тут использую make_response т.к. set_cookie метод объекта response без него получаю ошибку 'dict' object has no attribute 'set_cookie'
    # в остальных ответах фласк сам преобразует в json
    response = make_response(
        {'user_obj': user, 'isAuth': True, 'access_token': new_access_token})
    response.set_cookie('token', new_refresh_token, httponly=True,
                        max_age=30*24*60*60, samesite='None', secure=True, path='/api')
    return response


# обработка запроса на выход из системы
@app.route('/api/logout', methods=['GET'])
@jwt_required(refresh=True)
def logout():
    # получаем id юзера из токена 
    current_user = get_jwt_identity()
    # затираем токен в бд
    users_collection.update_one({'id': current_user}, {'$set': {'refresh_token': ''}})
    response = make_response({'message': 'User logged out successfully'})
    response.delete_cookie('token')
    return response


# защита эндпоинта для авторизованных пользователей
@app.route('/api/protected')
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    user_obj = users_collection.find_one({'id': user_id}, {'_id': 0})
    # кастылём удаляю пароль из ответа
    del user_obj['password']
    response = {'user_obj': user_obj, 'isAuth': True}
    print('protected')
    return response


# получение постов
# @app.route('/api/posts', methods=['GET', 'OPTIONS'])
# def get_posts():
#     page = int(request.args.get('page', 1))
#     page_size = int(request.args.get('page_size', 2))

# # добавить поле дата создания и тогда по ней можно сортироваться

#     # операция агрегации
#     pipeline = [
#         # поиск всех постов с информацией об авторе
#         {
#             '$lookup': {
#                 'from': 'users',
#                 'localField': 'author',
#                 'foreignField': '_id',
#                 'as': 'author'
#             }
#         },
#         # объединение данных о посте и авторе
#         {
#             '$unwind': '$author'
#         },
#         # сортировка по дате создания в порядке убывания
#         {
#             '$sort': {
#                 # 'created_at': -1
#                 'id': -1
#             }
#         },
#         # пропуск документов для реализации пагинации
#         {
#             # '$skip': page_size
#             '$skip': (page - 1) * page_size
#         },
#         # ограничение количества выдаваемых документов
#         {
#             '$limit': page_size
#         },
#         # исключение поля "_id" из документа автора
#         {
#             '$project': {
#                 'text': 1,
#                 'rating': 1,
#                 'author.username': 1,
#                 'author.img': 1,
#                 'author.id': 1,
#                 '_id': 0
#             }
#         }
#     ]

#     # выполнение операции агрегации
#     result = posts_collection.aggregate(pipeline)
#     print(posts_collection.find({}))
#     count = posts_collection.count_documents({})
#     posts = [post for post in result]
#     response = {'posts': posts, 'count': count}
#     # response.set_cookie('test', 'test', samesite='None', secure=True)
#     return response


# добавление поста
@app.route('/api/posts', methods=['POST'])
@jwt_required()
def add_post():
    author_id = get_jwt_identity()  # айди юзера из куки
    post_data = request.json
    post_text = post_data['text']
    print(f'id - {author_id}   msg - {post_text}')
    # получаем автора поста из коллекции users
    author = users_collection.find_one({'id': author_id}, {'_id': 1})
    print(author)

    # создаем новый документ в коллекции posts
    current_id = posts_collection.count_documents({}) + 1
    new_post = {
        "id": current_id,
        "text": post_text,
        "rating": 100,
        "author": author['_id']
    }
    # добавляем пост в бд
    posts_collection.insert_one(new_post)

    # возвращаем флаг создания поста
    return {'isCreate': True}


@app.route('/api/users', methods=['GET'])
# @jwt_required(locations=['headers', 'cookies'])
@jwt_required()
def get_users():
    # ошибку с ними получаю
    # current_user_id = get_jwt_identity()
    # print(current_user_id)
    users_list = []
    for user in users_collection.find({}, {'_id': 0, 'password': 0}):
        users_list.append(user)
    count = users_collection.count_documents({})
    response = {'users': users_list, 'count': count}
    return response


@app.route('/api/user/<int:user_id>', methods=['GET'])
@jwt_required()  # использование декоратора для проверки токена
def get_user(user_id):  # сюда передается айди профиля который мы просматриваем
    # получение идентификатора пользователя из токена тут получаю ошибку
    # verify_jwt_in_request()
    current_user_id = get_jwt_identity()  # айди юзера из куки
    print(f'current_user_id - {current_user_id}')
    print(f'user_id - {user_id}')
    user_info = users_collection.find_one(
        {'id': user_id}, {'_id': 0, 'password': 0})
    user_posts = posts_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author",
                    'foreignField': "_id",
                    'as': "author_info"
                }
        },
        {
            '$match': {
                "author_info.id": user_id
            }
        },
        # исключение полей
        {
            '$project': {
                'text': 1,
                # 'rating': 1,
                '_id': 0
            }
        }
    ])
    # создаём список из объекта бд
    user_posts = list(user_posts)
    # вычисляем и записываем количество постов в информацию о юзере
    user_info['posts_count'] = len(user_posts)
    # преобразовываем объект бд в список постов
    user_posts = [txt['text'] for txt in user_posts]
    if user_id == current_user_id:
        response = {'user_info': user_info,
                    'user_posts': user_posts, 'isMe': True}
    else:
        response = {'user_info': user_info,
                    'user_posts': user_posts, 'isMe': False}
    return response

# @app.route('/api/user', methods=['GET'])
# @jwt_required()  # использование декоратора для проверки токена
# def get_user():
#     # получение идентификатора пользователя из токена тут получаю ошибку
#     # verify_jwt_in_request()
#     current_user_id = get_jwt_identity()
#     print(f'current_user_id - {current_user_id}')
#     user_info = users_collection.find_one(
#         {'id': current_user_id}, {'_id': 0, 'password': 0})
#     user_posts = posts_collection.aggregate([
#         {
#             '$lookup':
#                 {
#                     'from': "users",
#                     'localField': "author",
#                     'foreignField': "_id",
#                     'as': "author_info"
#                 }
#         },
#         {
#             '$match': {
#                 "author_info.id": current_user_id
#             }
#         },
#         # исключение полей
#         {
#             '$project': {
#                 'text': 1,
#                 # 'rating': 1,
#                 '_id': 0
#             }
#         }
#     ])
#     # создаём список из объекта бд
#     user_posts = list(user_posts)
#     # вычисляем и записываем количество постов в информацию о юзере
#     user_info['posts_count'] = len(user_posts)
#     # преобразовываем объект бд в список постов
#     user_posts = [txt['text'] for txt in user_posts]
#     response = {'user_info': user_info, 'user_posts': user_posts}
#     print('user')
#     return response

#  айди в урле можно принимать и сравнивать его с айди из куки, если они одинаковые то передавать флаг это я и тогда профиль будет иметь возможность редактирования


@app.route('/api/user/<int:user_id>', methods=['POST', 'OPTIONS'])  # исправить передачу айди юзера
@jwt_required()  # использование декоратора для проверки токена
def upd_user(user_id):
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    status_text = data['statusText']
    print(f'status_text - {status_text}')
    print(f'userId - {user_id}')
    users_collection.update_one(
        {'id': user_id}, {'$set': {'statusText': status_text}})
    response = {'statusText': status_text}
    return response


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    app.run()
