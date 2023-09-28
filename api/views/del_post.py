# получение постов
from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
api_del_post = Blueprint('api_del_post', __name__)
# переменные из файла mongo.py
from mongo import posts_collection


@api_del_post.route('/del_post', methods=['POST'])
@jwt_required()
def del_post():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    post_id = data['post_id']
    print(f'post_id - {post_id}')
    try:
        posts_collection.delete_one({'_id': ObjectId(post_id)})
        response = post_id
    except:
        response = False
    return response