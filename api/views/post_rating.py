#  изменение рейтинга поста
from mongo import users_collection, posts_collection
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint, request
api_post_rating = Blueprint('api_post_rating', __name__)
# переменные из файла mongo.py


@api_post_rating.route('/post_rating', methods=['PUT'])
@jwt_required()
def post_rating():
    # получаем id юзера из токена
    current_user = get_jwt_identity()
    # получаем данные из запроса
    data = request.json
    # id поста
    post_id = data['post_id']
    # знак оценки юзера ( 1 = + , 0 = -)
    score = data['score']
    try:
        user_id = users_collection.find_one({'id': current_user}, {'_id': 1})
        post_rating = posts_collection.find_one(
            {'id': post_id}, {'_id': 0, 'rating': {'result': 1}})
        # print(type(post_rating['rating']['result']))
        rating = post_rating['rating']['result']

        # проверка есть ли уже оценка этого юзера у данного поста

        # тут надо работать с объектом пост_рейтинг что бы исключить еще один запрос к бд

        # делаем запрос к бд с поиском поста
        isScore = posts_collection.find_one(
            {'id': post_id, 'rating.usersRated.userId': user_id}, {'rating.usersRated.score': 1})
        # если есть такой пост продолжаем работу, если нет возвращаем старый рейтинг
        if isScore:
            # print(f'score - {isScore}')
            # тут получаем список всех юзеров кто поставил оценку
            print(f'score - {isScore["rating"]["usersRated"][0]["score"]}')
            print(f'user_id - {user_id["_id"]}')

            if isScore["rating"]["usersRated"][0]["score"] == score:
                print('РАВНО')
                # значение новой оценки равно значению уже имеющейся, возвращаем неизменённый рейтинг - rating
                response = {"new_rating": {"result": rating}}
                return response
            else:
                print('НЕ РАВНО')
                # если оценка противоположная, то изменяем рейтинг на новое значение и удаляем запись о пользователе из поля "usersRated"

                # обновление документа коллекции, удаляющее запись пользователя из поля "usersRated"
                posts_collection.update_one(
                    {"id": post_id},
                    {"$pull": {"rating.usersRated": {
                        "userId._id": user_id["_id"]}}}
                )

                # новое значение рейтинга зависит от оценки поставленной юзером
                new_rating = rating + 1 if score > 0 else rating - 1
                # обновляем рейтинг поста и записываем айди юзера кто поставил оценку
                posts_collection.update_one({'id': post_id}, {'$set': {"rating.result": new_rating}})
                response = {"new_rating": {"result": new_rating}}

        else:
            print('NOT')
            # новое значение рейтинга зависит от оценки поставленной юзером
            new_rating = rating + 1 if score > 0 else rating - 1
            # обновляем рейтинг поста и записываем айди юзера кто поставил оценку
            posts_collection.update_one({'id': post_id}, {'$set': {"rating.result": new_rating}, '$push': {
                "rating.usersRated": {"userId": user_id, "score": score}}})
            response = {"new_rating": {"result": new_rating}}
            return response

        # тут добавить обновление поля у юзера если он поставил плюс или минус посту, для подсчета общего количество поставленных оценок у юзера в лк

    except:
        response = {"msg": "Post not found"}
    return response
