# получение юзеров
from operator import attrgetter
import bson
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, users_collection
from flask import Blueprint, request
from bson import json_util

api_get_users = Blueprint('api_get_users', __name__)


@api_get_users.route('/users', methods=['GET'])  # добавить выдачу юзеров постранично
@jwt_required()
def get_users():
    #     for doc in result:
    #         print(doc['_id'], doc['total_result'])

    users_list = []
    for user in users_collection.find({}, {'password': 0}):
        # user['_id'] = json_util.dumps(user['_id'])
        # user['_id'] = user['_id'][10: -2]

        pipeline = [
            # поиск всех постов с информацией об авторе

            # получаем автора поста
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'author',
                    'foreignField': '_id',
                    'as': 'author'
                }
            },
            {
                "$match": {
                    "author.id": user['_id']
                }
            },
            # исключение поля "_id" из документа автора
            {
                '$project': {
                    'rating': {'result': 1}
                }
            }
        ]

        result = posts_collection.aggregate(pipeline)
        total_rating = 0
        for doc in result:
            # print(doc)
            total_rating = total_rating + doc['rating']['result']

        print('_id', user['_id'])
        user['_id'] = str(user['_id'])
        # user['_id'] = user['_id'][10: -2]
        user['rating'] = total_rating
        users_list.append(user)
    count = users_collection.count_documents({})
    # sorted(users_list, key=attrgetter('rating'), reverse=False)
    users_list = sorted(users_list, key=lambda x: x['rating'], reverse=True)
    print(users_list)
    response = {'users': users_list, 'count': count}
    return response
