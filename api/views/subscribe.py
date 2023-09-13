# получение постов
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import users_collection
api_subscribe = Blueprint('api_subscribe', __name__)
# переменные из файла mongo.py


# принимаем айди юзера на кого нужно подписатьсяё
@api_subscribe.route('/subscribe', methods=['PUT'])
@jwt_required()
def subscribe():
    # получаем id юзера из токена
    current_user = get_jwt_identity()
    # получаем данные из запроса
    data = request.json
    # получаем айди юзера на которого подписываемся
    to_user_id = int(data['to_user_id'])

    print(f'айди юзера - {current_user}')
    print(f'на кого подписан - {to_user_id}')

    try:
        users_collection.update_one({'id': to_user_id}, {'$push': {'subscribers': current_user}})
    except:
        print('error')


    # вернуть юзеров на кого ты подписан

    # вернуть флаг что ты подписан на этого юзера
    response = {'subs': True}
    return response