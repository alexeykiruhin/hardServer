# добавление комментария
from datetime import datetime
from flask import Blueprint, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_add_comment = Blueprint('api_add_comment', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection, comments_collection


@api_add_comment.route('/comment', methods=['POST'])
@jwt_required()
def add_comment():
    data = request.json
    author_id = get_jwt_identity()  # айди юзера из куки
    # получаем автора поста из коллекции users !!!!!  
    # нужно исправить путём добавление в jwt нормального айди
    author = users_collection.find_one({'id': author_id}, {'_id': 1})

    # получаем айди поста
    post_id = int(data['post_id'])
    print(f'post_id - {post_id}')
    real_post_id = posts_collection.find_one({'id': post_id}, {'_id': 1})
    print(f'real_post_id - {real_post_id}')
    real_post_id = real_post_id.get('_id')

    # получаем текст комментария
    comment_text = data['text']

    # создаем новый документ в коллекции comments
    new_comment = {
        "author_id": author['_id'],
        "post_id": real_post_id,
        "comment_text": comment_text,
        "created_at": datetime.now()
    }
    # добавляем коммент в бд
    out = comments_collection.insert_one(new_comment)
    comment_id = str(out.inserted_id)
    # возвращаем флаг создания поста
    response = make_response({'isCommented': comment_id})
    return response