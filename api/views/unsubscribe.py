# получение постов
from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
# переменные из файла mongo.py
from mongo import users_collection

api_unsubscribe = Blueprint('api_unsubscribe', __name__)


@api_unsubscribe.route('/unsubscribe', methods=['PUT'])
@jwt_required()
def unsubscribe():
    # получаем id юзера из токена
    current_user = get_jwt_identity()
    # получаем данные из запроса
    data = request.json
    # получаем айди юзера от которого отписываемся
    to_user_id = data['to_user_id']

    print(f'айди юзера - {current_user}')
    print(f'на кого подписан - {to_user_id}')

    try:
        users_collection.update_one({'_id': ObjectId(to_user_id)}, {"$pull": {"subscribers": ObjectId(current_user)}})
    except:
        print('error')

    # вернуть юзеров на кого ты подписан

    # вернуть флаг что ты подписан на этого юзера
    response = {'subs': False}
    return response
