# удаление комментария
from flask import Blueprint, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
# переменные из файла mongo.py
from mongo import users_collection
from bson import ObjectId

api_logout = Blueprint('api_logout', __name__)


@api_logout.route('/logout', methods=['GET'])
@jwt_required(refresh=True)
def logout():
    """Logout"""

    # получаем id юзера из токена
    current_user = get_jwt_identity()
    # затираем токен в бд
    users_collection.update_one({'id': current_user}, {'$set': {'refresh_token': ''}})
    response = make_response({'message': 'User logged out successfully'})
    response.delete_cookie('token')
    response.set_cookie('token', '', httponly=True,
                        max_age=30 * 24 * 60 * 60, samesite='None', secure=True, path='/api')
    return response
