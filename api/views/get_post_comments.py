# получение юзера
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_get_post_comments = Blueprint('api_get_post_comments', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection, comments_collection
from bson import json_util




@api_get_post_comments.route('/comments/<int:post_id>', methods=['GET'])
# @jwt_required()  # использование декоратора для проверки токена
def get_post_comments(post_id):  # сюда передается айди поста который мы просматриваем
    # находим настоящий айди поста
    realId = posts_collection.find_one({'id': post_id}, {'_id': 1})
    realId = realId['_id']
    comments = comments_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author_id",
                    'foreignField': "_id",
                    'as': "author"
                }
        },# объединение данных о комментарии и авторе
        {
            '$unwind': '$author'
        },
        {
            '$match': {
                "post_id": realId
            }
        },
        # исключение полей
        {
            '$project': {
                'comment_text': 1,
                'created_at': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 1,
            }
        }
    ])
    # собираем результат в список и отдаем
    out = [c for c in comments]
    # Проходим по каждому документу и сериализуем ObjectId
    for o in out:
        o['_id'] = json_util.dumps(o['_id'])
        o['_id'] = o['_id'][10: -2]
        print(o['_id'][10: -2])
    print(out)
    response = {    
            'comments': out
        }
    return response
