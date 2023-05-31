# получение постов
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
api_edit_comment = Blueprint('api_edit_comment', __name__)
# переменные из файла mongo.py
from mongo import comments_collection
from bson import json_util

@api_edit_comment.route('/edit_comment', methods=['POST'])
@jwt_required()
def del_post():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    comment_id = data['comment_id']
    decode_id = '{"$oid": "' + comment_id + '"}'
    decode_id = json_util.loads(decode_id)
    new_comment_text = data['new_comment_text']
    print(f'comment_id - {comment_id}')
    print(f'new_comment_text - {new_comment_text}')
    try:
        comments_collection.update_one({'_id': decode_id}, {'$set': {'comment_text': new_comment_text}})
        response = {'comment_id': comment_id, 'new_comment_text': new_comment_text}
    except:
        response = {'editComment': False}
    return response