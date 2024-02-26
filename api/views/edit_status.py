# удаление комментария
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
# переменные из файла mongo.py
from mongo import users_collection
from bson import ObjectId

api_edit_status = Blueprint('api_edit_status', __name__)


@api_edit_status.route('/user/<string:user_id>', methods=['POST'])
@jwt_required()
def edit_status(user_id):
    """Change Text status"""

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    status_text = data['statusText']
    print(f'status_text - {status_text}')
    print(f'userId - {user_id}')
    users_collection.update_one(
        {'_id': ObjectId(user_id)}, {'$set': {'statusText': status_text}})
    response = {'statusText': status_text}
    return response
