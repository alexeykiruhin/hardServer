#  изменение рейтинга поста
from bson import ObjectId
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint, request
api_post_rating = Blueprint('api_post_rating', __name__)
# переменные из файла mongo.py
from mongo import users_collection, posts_collection


@api_post_rating.route('/post_rating', methods=['PUT'])
@jwt_required()
def post_rating():
    # получаем id юзера из токена
    current_user = ObjectId(get_jwt_identity())
    # получаем данные из запроса
    data = request.json
    # id поста
    post_id = data['post_id']
    # знак оценки юзера ( 1 = + , 0 = -)
    score = data['score']
    print(f"post_id - {post_id} __ score - {score}")
    print(f"current_user - {current_user}")
    try:
        # находим юзера и забираем у него айди плюсы и минусы
        user = users_collection.find_one({'_id': current_user}, {'_id': 1, 'plus': 1, 'minus': 1})
        user_id = user['_id'] # _id юзера
        print(f'user - {user}')
        plus = user['plus'] # количество плюсов у юзера
        minus = user['minus'] # количество минусов у юзера
        # user_id = users_collection.find_one({'id': current_user}, {'_id': 1}) # _id юзера

        post_rating = posts_collection.find_one(
            {'_id': ObjectId(post_id)}, {'_id': 0, 'rating': {'result': 1}})
        # print(type(post_rating['rating']['result']))
        rating = post_rating['rating']['result']
        print(f'post_rating - {post_rating}')

        # проверка есть ли уже оценка этого юзера у данного поста

        # тут надо работать с объектом пост_рейтинг что бы исключить еще один запрос к бд

        # делаем запрос к бд с поиском поста
        isScore = posts_collection.find_one(
            {'_id': ObjectId(post_id), 'rating.usersRated.userId': ObjectId(user_id)}, {'rating.usersRated.score': 1})
        print(f'iscore - {isScore}')



        # ___________

        # Создайте запрос для агрегации
        # pip = [
        #     {
        #         "$match": {
        #             "_id": {
        #                 "$oid": post_id
        #             }
        #         }
        #     },
        #     {
        #         "$project": {
        #             "rating.usersRated": {
        #                 "$filter": {
        #                     "input": "$rating.usersRated",
        #                     "as": "user",
        #                     "cond": {
        #                         "$eq": ["$$user.userId.$oid", user_id]
        #                     }
        #                 }
        #             }
        #         }
        #     }
        # ]
        #
        # # Выполните запрос к базе данных
        # res = list(posts_collection.aggregate(pip))
        #
        # # Извлеките значение score, если оно существует
        # if res and "rating" in res[0] and "usersRated" in res[0]["rating"] and len(
        #         res[0]["rating"]["usersRated"]) > 0:
        #     score = res[0]["rating"]["usersRated"][0]["score"]
        #     print(f"Score для userId {user_id}: {score}")
        # else:
        #     print(f"Score для userId {user_id} не найден")

        # ______________

        # isScore = posts_collection.find_one(
        #     {'id': post_id, 'rating.usersRated.userId': user_id}, {'rating.usersRated.score': 1})
        # если есть такой пост продолжаем работу, если нет возвращаем старый рейтинг
        if isScore:
            # print(f'score - {isScore}')
            # тут получаем список всех юзеров кто поставил оценку
            print(f'score - {isScore["rating"]["usersRated"][0]["score"]}')
            print(f'user_id - {user_id}')

            if isScore["rating"]["usersRated"][0]["score"] == score:
                print('РАВНО')
                # значение новой оценки равно значению уже имеющейся, возвращаем неизменённый рейтинг - rating
                response = {"new_rating": {"result": {"result": rating}, 'post_id': post_id}}
                return response
            else:
                print('НЕ РАВНО')
                # если оценка противоположная, то изменяем рейтинг на новое значение и удаляем запись о пользователе из поля "usersRated"

                # обновление документа коллекции, удаляющее запись пользователя из поля "usersRated"
                posts_collection.update_one(
                    {"_id": ObjectId(post_id)},
                    {"$pull": {"rating.usersRated": {
                        "userId": ObjectId(user_id)}}}
                )

                # так же удаляем эту оценку из документа юзерс (из счётчика оценок юзера)

                if score > 0:
                    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'minus': minus - 1}})
                else:
                    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'plus': plus - 1}})


                # новое значение рейтинга зависит от оценки поставленной юзером
                new_rating = rating + 1 if score > 0 else rating - 1
                # обновляем рейтинг поста
                posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': {"rating.result": new_rating}})
            
                response = {"new_rating": {"result": {"result": new_rating}, 'post_id': post_id}}

        else:
            print('NOT')
            # новое значение рейтинга зависит от оценки поставленной юзером
            new_rating = rating + 1 if score > 0 else rating - 1
            # обновляем рейтинг поста и записываем айди юзера кто поставил оценку
            posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': {"rating.result": new_rating}, '$push': {
                "rating.usersRated": {"userId": user_id, "score": score}}})
            # posts_collection.update_one({'id': post_id}, {'$set': {"rating.result": new_rating}, '$push': {
            #     "rating.usersRated": {"userId": user_id, "score": score}}})
            
            # добавляем эту оценку в счётчик оценок у юзера
            if score > 0:
                users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'plus': plus + 1}})
            else:
                users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'minus': minus + 1}})

            response = {"new_rating": {"result": {"result": new_rating}, 'post_id': post_id}}
            return response

        # тут добавить обновление поля у юзера если он поставил плюс или минус посту, для подсчета общего количество поставленных оценок у юзера в лк

    except:
        response = {"msg": "Post not found"}
    return response
