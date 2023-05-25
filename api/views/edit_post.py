# получение постов
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
api_edit_post = Blueprint('api_edit_post', __name__)
# переменные из файла mongo.py
from mongo import posts_collection


@api_edit_post.route('/edit_post', methods=['POST'])
@jwt_required()
def del_post():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    post_id = data['post_id']
    new_post_text = data['new_post_text']
    print(f'post_id - {post_id}')
    print(f'new_post_text - {new_post_text}')
    try:
        posts_collection.update_one({'id': post_id}, {'$set': {'text': new_post_text}})
        response = {'post_id': post_id, 'new_post_text': new_post_text}
    except:
        response = {'editPost': False}
    return response