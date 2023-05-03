# получение юзера
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_get_postView = Blueprint('api_get_postView', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection



@api_get_postView.route('/post/<int:post_id>', methods=['GET'])
# @jwt_required()  # использование декоратора для проверки токена
def get_user(post_id):  # сюда передается айди поста который мы просматриваем
    # получение идентификатора пользователя из токена тут получаю ошибку
    # verify_jwt_in_request()
    # current_user_id = get_jwt_identity()  # айди юзера из куки
    # print(f'current_user_id - {current_user_id}')
    # print(f'user_id - {user_id}')
    # post_info = posts_collection.find_one(
    #     {'id': post_id}, {'_id': 0, 'password': 0})

    post_info = posts_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author",
                    'foreignField': "_id",
                    'as': "author"
                }
        },# объединение данных о посте и авторе
        {
            '$unwind': '$author'
        },
        {
            '$match': {
                "id": post_id
            }
        },
        # исключение полей
        {
            '$project': {
                'id': 1,
                'text': 1,
                # 'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 0,
                'rating': {'result': 1}
            }
        }
    ])
    # создаём список из объекта бд
    # user_posts = list(user_posts)
    # all_rating = sum([r['rating']['result'] for r in user_posts])
    # print(f'rating post - {all_rating}')
    # вычисляем и записываем количество постов в информацию о юзере
    # user_info['posts_count'] = len(user_posts)
    # преобразовываем объект бд в список постов
    # user_posts = [txt['text'] for txt in user_posts]
    #  айди в урле сравниваем с айди из куки, если они одинаковые то передавать
    #  флаг это я и тогда профиль будет иметь возможность редактирования
    # is_me = True if user_id == current_user_id else False

    
    print(f'info - {post_info}')
    post = [p for p in post_info]
    print(f'info - {post[0]}')


    response = {    
            'post_info': post[0]
        }
    return response
