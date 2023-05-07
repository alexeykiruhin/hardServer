# добавление поста
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_add_post = Blueprint('api_add_post', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection


@api_add_post.route('/posts', methods=['POST'])
@jwt_required()
def add_post():
    author_id = get_jwt_identity()  # айди юзера из куки
    post_data = request.json
    post_text = post_data['text']
    print(f'id - {author_id}   msg - {post_text}')
    # получаем автора поста из коллекции users
    author = users_collection.find_one({'id': author_id}, {'_id': 1})
    print(author)

    # создаем новый документ в коллекции posts
    current_id = posts_collection.count_documents({}) + 1
    new_post = {
        "id": current_id,
        "text": post_text,
        "rating": {
            "result": 100,
            "usersRated": []
        },
        "author": author['_id']
    }
    # добавляем пост в бд
    posts_collection.insert_one(new_post)

    # возвращаем флаг создания поста
    return {'isCreate': True}
