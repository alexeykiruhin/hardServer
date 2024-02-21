from bson import ObjectId
from flask import Blueprint

from api.functions.change_id import change_id
from mongo import posts_collection  # переменные из файла mongo.py

api_get_post_view = Blueprint('api_get_post_view', __name__)


@api_get_post_view.route('/post/<string:post_id>', methods=['GET'])
def get_post_view(post_id):
    """Получение поста (просмотр поста)"""
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

    post = change_id(post_info)
    return post
