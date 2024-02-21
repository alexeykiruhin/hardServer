# добавление комментария
import datetime
from bson import ObjectId
from flask import Blueprint, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from api.functions.change_id import change_id

api_add_comment = Blueprint('api_add_comment', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection, comments_collection


@api_add_comment.route('/comment', methods=['POST'])
@jwt_required()
def add_comment():
    data = request.json
    author_id = ObjectId(get_jwt_identity())  # айди юзера из куки
    comment_data = data['comment_data']
    post_id = ObjectId(comment_data['post_id'])

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
    # out = comments_collection.insert_one(new_comment)
    out = comments_collection.insert_one(new_comment)
    out_res = comments_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author_id",
                    'foreignField': "_id",
                    'as': "author"
                }
        },
        # объединение данных о комментарии и авторе
        {
            '$unwind': '$author'
        },
        # фильтр по айди комментария
        {
            '$match': {
                "_id": out.inserted_id
            }
        },
        # исключение полей
        {
            '$project': {
                'text': 1,
                'created_at': 1,
                'author.username': 1,
                'author.img': 1,
                'author._id': 1,
                '_id': 1,
            }
        }
    ])
    out_res = change_id(out_res)
    return out_res
