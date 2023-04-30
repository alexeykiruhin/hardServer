# получение юзера
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_get_user = Blueprint('api_get_user', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection



@api_get_user.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()  # использование декоратора для проверки токена
def get_user(user_id):  # сюда передается айди профиля который мы просматриваем
    # получение идентификатора пользователя из токена тут получаю ошибку
    # verify_jwt_in_request()
    current_user_id = get_jwt_identity()  # айди юзера из куки
    print(f'current_user_id - {current_user_id}')
    print(f'user_id - {user_id}')
    user_info = users_collection.find_one(
        {'id': user_id}, {'_id': 0, 'password': 0})
    # подсчитываем количество подписчиков
    user_info['subscribers'] = len(user_info['subscribers'])

    user_posts = posts_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author",
                    'foreignField': "_id",
                    'as': "author_info"
                }
        },
        {
            '$match': {
                "author_info.id": user_id
            }
        },
        # исключение полей
        {
            '$project': {
                'text': 1,
                # вытаскиваем ещё и рейтинг поста потом ниже его суммируем и отдаём
                'rating.result': 1,
                '_id': 0
            }
        }
    ])
    # создаём список из объекта бд
    user_posts = list(user_posts)
    all_rating = sum([r['rating']['result'] for r in user_posts])
    # print(f'rating post - {all_rating}')
    # вычисляем и записываем количество постов в информацию о юзере
    user_info['posts_count'] = len(user_posts)
    # преобразовываем объект бд в список постов
    user_posts = [txt['text'] for txt in user_posts]
    #  айди в урле сравниваем с айди из куки, если они одинаковые то передавать
    #  флаг это я и тогда профиль будет иметь возможность редактирования
    is_me = True if user_id == current_user_id else False
    print(f'info - {user_info}')
    response = {
            'user_info': user_info,
            'user_posts': user_posts,
            'all_rating': all_rating,
            'isMe': is_me
        }
    return response
