# удаление комментария
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
api_del_сomment = Blueprint('api_del_сomment', __name__)
# переменные из файла mongo.py
from mongo import comments_collection
from bson import json_util


@api_del_сomment.route('/del_comment', methods=['POST'])
@jwt_required()
def del_post():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    comment_id = data['comment_id']
    decode_id = '{"$oid": "' + comment_id + '"}'
    print(f'comment_id - {json_util.loads(decode_id)}')
    try:
        comments_collection.delete_one({'_id': json_util.loads(decode_id)})
        response = {'statusDeletePost': True}
    except:
        response = {'statusDeletePost': False}
    return response