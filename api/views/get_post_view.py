# получение юзера
from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, users_collection  # переменные из файла mongo.py

api_get_post_view = Blueprint('api_get_post_view', __name__)


@api_get_post_view.route('/post/<string:post_id>', methods=['GET'])
# @jwt_required()  # использование декоратора для проверки токена
def get_post_view(post_id):
    # сюда передается айди поста который мы просматриваем
    post_id = ObjectId(post_id)
    post_info = posts_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author",
                    'foreignField': "_id",
                    'as': "author"
                }
        },  # объединение данных о посте и авторе
        # получаем теги поста
        {
            '$lookup': {
                'from': 'tags',
                'localField': 'tags',
                'foreignField': '_id',
                'as': 'tags'
            }
        },
        {
            '$unwind': '$author'
        },
        {
            '$match': {
                "_id": post_id
            }
        },
        # исключение полей
        {
            '$project': {
                'text': 1,
                'subject': 1,
                # 'rating': 1,
                'img': 1,
                'author.username': 1,
                'author.img': 1,
                'author._id': 1,
                '_id': 1,
                'rating': {'result': 1},
                'tags.tag_name': 1
            }
        }
    ])

    post = [p for p in post_info]

    post[0]['id'] = str(post[0]['_id'])
    del post[0]['_id']
    post[0]['author']['id'] = str(post[0]['author']['_id'])
    del post[0]['author']['_id']

    response = {
        'post_info': post[0]
    }
    print(post[0])
    return response
