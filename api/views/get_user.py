# получение юзера
from bson import ObjectId
from flask import Blueprint, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, users_collection

api_get_user = Blueprint('api_get_user', __name__)


# переменные из файла mongo.py


@api_get_user.route('/user/<string:user_id>', methods=['GET'])
@jwt_required()  # использование декоратора для проверки токена
def get_user(user_id):  # сюда передается айди профиля который мы просматриваем
    # получение идентификатора пользователя из токена тут получаю ошибку
    # verify_jwt_in_request()
    current_user_id = get_jwt_identity()  # айди юзера из куки
    # print(f'current_user_id - {current_user_id}')
    # print(f'user_id - {user_id}')
    user_info = users_collection.find_one(
        {'_id': ObjectId(user_id)}, {'password': 0})
    # проверка подписан ли юзер на юзера на чью страницу зашел
    is_bubscribed = True if current_user_id in user_info['subscribers'] else False
    # записываем в юзерс инфо значение о подписке
    user_info['is_sub'] = is_bubscribed
    # подсчитываем количество подписчиков
    user_info['subscribers'] = len(user_info['subscribers'])
    user_info['id'] = str(user_info['_id'])
    del user_info['_id']

    print(user_id)
    user_posts = posts_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author",
                    'foreignField': "_id",
                    'as': "author"
                }
        },
        # получаем теги поста
        {
            '$lookup':
                {
                    'from': 'tags',
                    'localField': 'tags',
                    'foreignField': '_id',
                    'as': 'tags'
                }
        },
        {
            '$match': {
                "author._id": ObjectId(user_id)
            }
        },
        # объединение данных о посте и авторе
        {
            '$unwind': '$author'
        },
        # исключение полей
        {
            '$project': {
                'text': 1,
                # вытаскиваем ещё и рейтинг поста потом ниже его суммируем и отдаём
                'rating.result': 1,
                '_id': 1,
                'subject': 1,
                # 'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author._id': 1,
                'tags.tag_name': 1
            }
        }
    ])
    # создаём список из объекта бд
    user_posts = list(user_posts)
    for user_post in user_posts:
        user_post['id'] = str(user_post['_id'])
        del user_post['_id']

    for post in user_posts:
        # author, перобразование _id в строку
        if 'author' in post:
            post['author']['id'] = str(post['author']['_id'])
            del post['author']['_id']
    print(f'user_posts_first - {user_posts}')
    all_rating = sum([r['rating']['result'] for r in user_posts])
    # print(f'rating post - {all_rating}')
    # вычисляем и записываем количество постов в информацию о юзере
    user_info['posts_count'] = len(user_posts)
    # преобразовываем объект бд в список постов
    # user_posts = [[txt['text'], str(txt['_id'])] for txt in user_posts]
    print(user_posts)
    #  айди в урле сравниваем с айди из куки, если они одинаковые то передавать
    #  флаг это я и тогда профиль будет иметь возможность редактирования
    is_me = True if user_id == current_user_id else False

    print(f'info - {user_info}')

    response = make_response({
        'user_info': user_info,
        'user_posts': user_posts,
        'all_rating': all_rating,
        'isMe': is_me
    })
    return response
