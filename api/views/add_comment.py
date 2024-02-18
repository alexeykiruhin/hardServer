# добавление комментария
import datetime
from bson import ObjectId
from flask import Blueprint, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_add_comment = Blueprint('api_add_comment', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection, comments_collection


@api_add_comment.route('/comment', methods=['POST'])
@jwt_required()
def add_comment():
    data = request.json
    author_id = ObjectId(get_jwt_identity())  # айди юзера из куки
    print('author_id', author_id)
    comment_data = data['comment_data']
    post_id = ObjectId(comment_data['post_id'])
    print(f'post_id - {post_id}')

    # получаем текст комментария
    comment_text = comment_data['text']

    # создаем новый документ в коллекции comments
    new_comment = {
        "author_id": author_id,
        "post_id": post_id,
        "text": comment_text,
        "created_at": datetime.datetime.now()
    }
    # добавляем коммент в бд
    out = comments_collection.insert_one(new_comment)
    comment_id = str(out.inserted_id)
    # возвращаем флаг создания поста
    response = make_response({'isCommented': comment_id})
    # возвразать нужно целый коммент, что бы на клиенте его приклеить к уже имеющимся
    return response