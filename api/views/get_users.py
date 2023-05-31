# получение юзеров
import bson
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import users_collection
from flask import Blueprint, request
api_get_users = Blueprint('api_get_users', __name__)

@api_get_users.route('/users', methods=['GET']) # добавить выдачу юзеров постранично
@jwt_required()
def get_users():
    users_list = []
    for user in users_collection.find({}, {'_id': 0, 'password': 0}):
        users_list.append(user)
    count = users_collection.count_documents({})
    response = {'users': users_list, 'count': count}
    return response
