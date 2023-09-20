import random
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from mongo import users_collection  # переменные из файла mongo.py

api_registration = Blueprint('api_registration', __name__)


@api_registration.route('/register', methods=['POST'])
def registration():
    """Registration blueprint"""
    # получаем данные из запроса
    print(request.json)
    data = request.json
    # проверяем, что такой пользователь не существует
    user = users_collection.find_one({'email': data['email']}, {'_id': 0})
    # try:
    #     user = users_collection.find_one({'email': data['email']}, {'_id': 0})
    # finally:
    #     # не существует
    #     user = False
    if user:
        # существует
        return {'error': 'User already exists'}
    else:
        # создаем нового пользователя
        if data['username'] and data['password']:
            #  проверяем что логин и пароль передали
            usr = {
                "email": data['email'],
                "username": data['username'],
                "password": data['password'],  # сделать хеширование
                "img": f"https://randomuser.me/api/portraits/men/{random.randint(1, 100)}.jpg",  # временная ава
                "rating": 0,
                "statusText": "newbie",
                "refresh_token": "",
                "plus": 0,
                "minus": 0,
                "subscribers": []
            }
            users_collection.insert_one(usr)
            return {'isReg': True}
        else:
            return {'isReg': False}
