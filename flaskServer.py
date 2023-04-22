import datetime
import random

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import mongo

# переменные из файла mongo.py
users_collection = mongo.users
posts_collection = mongo.posts

app = Flask(__name__)
app.secret_key = 'mysecretkey'
CORS(app, supports_credentials=True)
# задаем секретный ключ для подписи токена
app.config['JWT_SECRET_KEY'] = '23sa3501080X'
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
# app.config['JWT_REFRESH_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_REFRESH_COOKIE_NAME'] = 'token'

# app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Ожидаем токен в заголовках
# app.config['JWT_HEADER_NAME'] = 'Authorization'  # Имя заголовка, в котором ожидается токен
# app.config['JWT_REFRESH_TOKEN_LOCATION'] = ['cookies']  # Ожидаем refresh-токен в куках
# app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'  # Имя куки, в которой ожидается refresh-токен


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
        return jsonify({'error': 'User already exists'})
    else:
        # создаем нового пользователя
        if data['username'] and data['password']:
            #  проверяем что логин и пароль передали
            print(users_collection.count_documents({}))
            length_users = users_collection.count_documents({})
            usr = {
                "id": length_users + 1,
                "username": data['username'],
                "password": data['password'],
                "img": f"https://randomuser.me/api/portraits/men/{random.randint(1, 100)}.jpg",
                "rating": 100,
                "statusText": "newbie"
            }
            users_collection.insert_one(usr)
            return jsonify({'isReg': True})
        else:
            return jsonify({'isReg': False})


# обработка запроса на авторизацию пользователя
@app.route('/api/login', methods=['POST'])
def login():
    # получаем данные из запроса
    data = request.json
    # ищем пользователя в базе данных
    user = users_collection.find_one({'username': data['username']}, {'_id': 0, 'statusText': 0, 'rating': 0})
    if user is None:
        print(f'Пользователя с логином {data["username"]} не существует')
        return jsonify({'messageError': f'Пользователя с логином {data["username"]} не существует'}), 401
    # проверяем пароль
    if user['password'] == data['password']:
        # создаем токен, вынести в отдельную функцию
        access_token = create_access_token(identity=user['id'], expires_delta=datetime.timedelta(seconds=20))
        refresh_token = create_refresh_token(identity=user['id'], expires_delta=datetime.timedelta(days=30))
        # print(access_token)
        # после проверки пароля удаляю его из объекта юзера, перед ответом на клиент
        del user['password']
        response = jsonify(
            {'user_obj': user, 'isAuth': True, 'access_token': access_token, 'refresh_token': refresh_token})
        # response.set_cookie('refresh_token', refresh_token, httponly=True, max_age=30*24*60*60, samesite='None', secure=True, path='/api')
        response.set_cookie('token', refresh_token, httponly=True, max_age=30*24*60*60, samesite='None', secure=True, path='/api')
        return response
    # возвращаем ошибку
    print('Неверный пароль')
    return jsonify({'messageError': 'Неверный пароль'}), 401

# Эндпоинт для обновления access token по refresh token
@app.route('/api/refresh', methods=['GET'])
@jwt_required(refresh=True)
# @jwt_required(refresh=True, locations=['cookies'])
# @jwt_required(refresh=True, locations=['headers', 'cookies'])
def refresh():
    print(f"cookie  -  {request.cookies.get('token')}")
    current_user = get_jwt_identity()
    print(f'user - {current_user}')
    # получаем данные юзера
    user = users_collection.find_one({'id': current_user}, {'_id': 0, 'password': 0})
    # print(f'user - {user}')
    new_access_token = create_access_token(identity=current_user, expires_delta=datetime.timedelta(seconds=20))
    new_refresh_token = create_refresh_token(identity=current_user, expires_delta=datetime.timedelta(days=30))
    print('новые токены сгенерированы')
    response = jsonify({'user_obj': user, 'isAuth': True, 'access_token': new_access_token})
    # response.set_cookie('refresh_token', new_refresh_token, httponly=False, max_age=30*24*60*60, samesite=None, secure=True, path='/')
    response.set_cookie('token', new_refresh_token, httponly=True, max_age=30*24*60*60, samesite='None', secure=True, path='/api')
    return response


# обработка запроса на выход из системы
@app.route('/api/logout')
def logout():
    # logout logic
    return jsonify({'message': 'User logged out successfully'})


# защита эндпоинта для авторизованных пользователей
@app.route('/protected')
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    user_obj = users_collection.find_one({'id': user_id}, {'_id': 0})
    # кастылём удаляю пароль из ответа
    del user_obj['password']
    response = jsonify({'user_obj': user_obj, 'isAuth': True})
    print('protected')
    return response


# получение постов
@app.route('/api/posts', methods=['GET', 'OPTIONS'])
def get_posts():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 2))

    # операция агрегации
    pipeline = [
        # поиск всех постов с информацией об авторе
        {
            '$lookup': {
                'from': 'users',
                'localField': 'author',
                'foreignField': '_id',
                'as': 'author'
            }
        },
        # объединение данных о посте и авторе
        {
            '$unwind': '$author'
        },
        # сортировка по дате создания в порядке убывания
        {
            '$sort': {
                'created_at': -1
            }
        },
        # пропуск документов для реализации пагинации
        {
            '$skip': (page - 1) * page_size
        },
        # ограничение количества выдаваемых документов
        {
            '$limit': page_size
        },
        # исключение поля "_id" из документа автора
        {
            '$project': {
                'text': 1,
                'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 0
            }
        }
    ]

    # выполнение операции агрегации
    result = posts_collection.aggregate(pipeline)
    count = posts_collection.count_documents({})
    posts = [post for post in result]
    response = jsonify({'posts': posts, 'count': count})
    # response.set_cookie('test', 'test', samesite='None', secure=True)
    return response


# добавление поста
@app.route('/api/posts', methods=['POST'])
@jwt_required()
def add_post():
    post_data = request.json
    author_id = post_data['author_id']
    post_text = post_data['text']
    print(f'id - {author_id}   msg - {post_text}')
    # получаем автора поста из коллекции users
    author = users_collection.find_one({'id': author_id}, {'_id': 1})
    print(author)
    # return jsonify('OK')

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

    # возвращаем id добавленного поста
    return jsonify({'isCreate': True})


@app.route('/api/users', methods=['GET', 'OPTIONS'])
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
    response = jsonify({'users': users_list, 'count': count})
    return response


@app.route('/api/user/<int:user_id>', methods=['GET', 'OPTIONS'])
@jwt_required()  # использование декоратора для проверки токена
def get_user(user_id):
    # получение идентификатора пользователя из токена тут получаю ошибку
    # current_user_id = get_jwt_identity()
    # print(current_user_id)
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
    response = jsonify({'user_info': user_info, 'user_posts': user_posts})
    return response


@app.route('/api/user/<int:user_id>', methods=['POST', 'OPTIONS'])
@jwt_required()  # использование декоратора для проверки токена
def upd_user(user_id):
    # получаем данные из запроса
    data = request.json
    status_text = data['statusText']
    print(f'status_text - {status_text}')
    print(f'userId - {user_id}')
    users_collection.update_one(
        {'id': user_id}, {'$set': {'statusText': status_text}})
    response = jsonify({'statusText': status_text})
    return response


@app.after_request
def add_cors_headers(response):
    # response.headers.add('Access-Control-Allow-Origin',
    #                      'http://localhost:3000')
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    app.run()
