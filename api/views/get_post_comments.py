# получение юзера
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_get_post_comments = Blueprint('api_get_post_comments', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection, comments_collection



@api_get_post_comments.route('/comments/<int:post_id>', methods=['GET'])
# @jwt_required()  # использование декоратора для проверки токена
def get_post_comments(post_id):  
    # сюда передается айди поста который мы просматриваем
    realId = posts_collection.find_one({'id': post_id}, {'_id': 1})
    print(realId['_id'])
    comments = comments_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author_id",
                    'foreignField': "_id",
                    'as': "author"
                }
        },# объединение данных о посте и авторе
        {
            '$unwind': '$author'
        },
        {
            '$match': {
                "post_id": realId['_id']
            }
        },
        # исключение полей
        {
            '$project': {
                # 'id': 1,
                'comment_text': 1,
                # 'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 0,
                # 'rating': {'result': 1}
            }
        }
    ])

    out = [p for p in comments]
    print(out)
    response = {    
            'comments': out
        }
    return response
