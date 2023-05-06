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

    # post_info = posts_collection.aggregate([
    #     {
    #         '$lookup':
    #             {
    #                 'from': "users",
    #                 'localField': "author",
    #                 'foreignField': "_id",
    #                 'as': "author"
    #             }
    #     },# объединение данных о посте и авторе
    #     {
    #         '$unwind': '$author'
    #     },
    #     {
    #         '$match': {
    #             "id": post_id
    #         }
    #     },
    #     # исключение полей
    #     {
    #         '$project': {
    #             'id': 1,
    #             'text': 1,
    #             # 'rating': 1,
    #             'author.username': 1,
    #             'author.img': 1,
    #             'author.id': 1,
    #             '_id': 0,
    #             'rating': {'result': 1}
    #         }
    #     }
    # ])

    # post = [p for p in post_info]

    response = {    
            'comments': 'tut comment'
        }
    return response
