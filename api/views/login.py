import datetime

import bcrypt
from flask import Blueprint, make_response, request
from flask_jwt_extended import create_access_token, create_refresh_token
from mongo import users_collection

api_login = Blueprint('api_login', __name__)


# переменные из файла mongo.py


@api_login.route('/login', methods=['POST'])
def login():
    """Эндпоинт для логина"""
    # получаем данные из запроса
    data = request.json
    # ищем пользователя в базе данных
    user = users_collection.find_one({'username': data['username']}, {'statusText': 0, 'rating': 0, 'refresh_token': 0})
    if user is None:
        print(f'Пользователя с логином {data["username"]} не существует')
        return {'messageError': f'Пользователя с логином {data["username"]} не существует'}, 401
    # проверяем пароль
    # Хеш пароля, сохраненный в базе данных
    stored_password_hash = user['password']
    print('stored_password_hash', stored_password_hash)

    # Пароль, полученный от клиента
    client_password = data['password']
    print('client_password', client_password)

    print('крипт', bcrypt.checkpw(client_password.encode('utf-8'), stored_password_hash))
    # Сравнение хешей
    # if user['password'] == data['password']:
    if bcrypt.checkpw(client_password.encode('utf-8'), stored_password_hash):
        print('ХЕШИ СРАВНИЛИСЬ')
        # создаем токен, вынести в отдельную функцию
        access_token = create_access_token(
            identity=str(user['_id']), expires_delta=datetime.timedelta(seconds=5))
        refresh_token = create_refresh_token(
            identity=str(user['_id']), expires_delta=datetime.timedelta(days=30))
        # добавляем токен в бд
        users_collection.update_one({'username': data['username']}, {
            '$set': {'refresh_token': refresh_token}})
        # после проверки пароля удаляю его из объекта юзера, перед ответом на клиент
        del user['password']
        user['subscribers'] = [str(u) for u in user['subscribers']]
        # Objectid переводим в строку
        user['_id'] = str(user['_id'])
        # записываем айди из монго дб в переменную id
        user['id'] = user['_id']
        # тут использую make_response т.к. set_cookie метод объекта response без него получаю ошибку 'dict' object
        # has no attribute 'set_cookie' в остальных ответах фласк сам преобразует в json
        response = make_response({'user_obj': user, 'isAuth': True,
                                  'access_token': access_token, 'refresh_token': refresh_token})

        response.set_cookie('token', refresh_token, httponly=True, max_age=30 * 24 * 60 * 60,
                            samesite='None', secure=True, path='/api')
        return response
    else:
        print('Неверный пароль')
        return {'messageError': 'Неверный пароль'}, 401
