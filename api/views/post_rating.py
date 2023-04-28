#  изменение рейтинга поста
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint, request
api_post_rating = Blueprint('api_post_rating', __name__)
# переменные из файла mongo.py
from mongo import users_collection, posts_collection


@api_post_rating.route('/post_rating', methods=['PUT'])
@jwt_required()
def post_rating():
    # получаем id юзера из токена 
    current_user = get_jwt_identity()
    # получаем данные из запроса
    data = request.json
    # post_id = data.post_id
    post_id = data['post_id']
    # score = data.score
    score = data['score']
    print(f'postId - {post_id}')
    print(f'postId - {score}')
    try:
        user_id = users_collection.find_one({'id': current_user}, {'_id': 1})
        post_rating = posts_collection.find_one({'id': post_id},{'_id': 0, 'rating': {'result': 1}})
        rating = int(post_rating['rating']['result'])
        if score > 0:
            new_rating = rating + 1
            # posts_collection.update_one({'id': post_id}, {'$set': { "rating.result": new_rating }, '$push': { "rating.usersRated": { "userId": user_id, "score": score } }})
        else:
            new_rating = rating - 1
        print(f'rating - {rating}')
        posts_collection.update_one({'id': post_id}, {'$set': { "rating.result": new_rating }, '$push': { "rating.usersRated": { "userId": user_id, "score": score } }})
        # response = {"new_rating": new_rating}
        response = {"new_rating": {"result": new_rating}}
    except:
        response = {"msg": "Post not found"}
    return response
    # найти данный пост и проверить, есть ли в нем оценка данного юзера? если нет забираем итоговый рейтинг, если есть возвращаем текущую оценку
    # нужно предусмотреть что юзер может поставить сначала + а потом передумать и поставить - или вообще убрать оценку
    # обдумать каким образом ограничить изменение рейтинга только один раз на пользователя

    # {
    #     "_id": {
    #         "$oid": "6431e23a84b894494daed234"
    #     },
    #     "id": 1,
    #     "text": "Интересные у тебя татуировки на ногах. Что они означают? Это варикоз.",
    #     "rating": {
    #         "result": 87,
    #         "usersRated": [
    #             { # первый элемент массива
    #                 "userId": 1, # пока в бд это id а не _id
    #                 "score": 0 # 0 или 1
    #             }
    #         ]
    #     },
    #     "author": {
    #         "$oid": "64300f6c84b894494daed20a"
    #     }
    # }
