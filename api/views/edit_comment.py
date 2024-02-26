# редактирование комментария
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
# переменные из файла mongo.py
from mongo import comments_collection
from bson import ObjectId

api_edit_comment = Blueprint('api_edit_comment', __name__)


@api_edit_comment.route('/edit_comment', methods=['POST'])
@jwt_required()
def edit_comment():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    print('EDIT - ', data)
    comment_data = data['comment_data']
    try:
        out = comments_collection.update_one(
            {'_id': ObjectId(comment_data['comment_id'])},
            {'$set': {'text': comment_data['text']}}
        )
        print('OUT', out)
        response = {'id': comment_data["comment_id"], 'text': comment_data['text']}
    except:
        response = {'editComment': False}
    return response
