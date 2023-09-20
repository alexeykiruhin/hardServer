from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from mongo import users_collection
import random

api_registration = Blueprint('api_registration', __name__)
# переменные из файла mongo.py
from bson import json_util


@api_registration.route('/register', methods=['POST'])
@jwt_required()
def registration():
    """Registration blueprint"""
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
