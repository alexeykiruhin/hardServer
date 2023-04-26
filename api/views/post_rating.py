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
    response = {"msg": "OK"}
    return response
    # найти данный пост и проверить, есть ли в нем оценка данного юзера? если нет забираем итоговый рейтинг, если есть возвращаем текущую оценку
    # нужно предусмотреть что юзер может поставить сначала + а потом передумать и поставить - или вообще убрать оценку
    try:
        post = posts_collection.find_one({'id': post_id}, {'rating': 1, 'usersRated': 1})
    except:
        return {"message": "Post not found"}
    # обдумать каким образом ограничить изменение рейтинга только один раз на пользователя
    
    if score:
        userScore = 1
    else:
        userScore = -1

    posts_collection.update_one({'id': post_id}, {'$set': {'result': status_text}})

    {
        "_id": {
            "$oid": "6431e23a84b894494daed234"
        },
        "id": 1,
        "text": "Интересные у тебя татуировки на ногах. Что они означают? Это варикоз.",
        "rating": {
            "result": 87,
            "usersRated": {
                "id": 1,
                "score": True
            }
        },
        "author": {
            "$oid": "64300f6c84b894494daed20a"
        }
    }