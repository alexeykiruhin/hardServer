# получение постов
from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
# переменные из файла mongo.py
from mongo import users_collection

api_subscribe = Blueprint('api_subscribe', __name__)


# принимаем айди юзера на кого нужно подписатьсяё
@api_subscribe.route('/subscribe', methods=['PUT'])
@jwt_required()
def subscribe():
    # получаем id юзера из токена
    current_user = get_jwt_identity()
    # получаем данные из запроса
    data = request.json
    # получаем айди юзера на которого подписываемся
    to_user_id = data['to_user_id']
    subscribers = 0

    print(f'айди юзера - {current_user}')
    print(f'на кого подписан - {to_user_id}')

    try:
        users_collection.update_one({'_id': ObjectId(to_user_id)}, {'$push': {'subscribers': ObjectId(current_user)}})
        # забираем новое количество подписчиков
        subscribers = len(users_collection.find_one({'_id': ObjectId(current_user)}, {'subscribers': 1}))
        print(f'subscribe - {subscribers}')
    except:
        print('error')

    # вернуть юзеров на кого ты подписан

    # вернуть флаг что ты подписан на этого юзера
    response = {'subs': True, 'subscribers': subscribers}
    return response
