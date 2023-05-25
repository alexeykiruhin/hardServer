# получение постов
import bson
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection
from flask import Blueprint, request
api_get_subs_posts = Blueprint('api_get_subs_posts', __name__)
# переменные из файла mongo.py

# добавить проверку на регистрацию, подписки не может быть у анона


@api_get_subs_posts.route('/subs_posts', methods=['GET'])
@jwt_required()
def get_subs_posts():
    # получаем id юзера из токена
    current_user = get_jwt_identity()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 2))
    print(f'current_user - {current_user}')

    # операция агрегации
    pipeline = [
        # поиск всех постов с информацией об авторе
        {
            '$lookup': {
                'from': 'users',
                'localField': 'author',
                'foreignField': '_id',
                'as': 'author'
            }
        },
        # получаем теги поста
        {
            '$lookup': {
                'from': 'tags',
                'localField': 'tags',
                'foreignField': '_id',
                'as': 'tags'
            }
        },
        {
            "$match": {
                "author.subscribers": {"$in": [current_user]}
            }
        },
        # объединение данных о посте и авторе
        {
            '$unwind': '$author'
        },
        # сортировка по дате создания в порядке убывания
        {
            '$sort': {
                # 'created_at': -1
                'id': -1
            }
        },
        # пропуск документов для реализации пагинации
        {
            # '$skip': page_size
            '$skip': (page - 1) * page_size
        },
        # ограничение количества выдаваемых документов
        {
            '$limit': page_size
        },
        # исключение поля "_id" из документа автора
        {
            '$project': {
                'id': 1,
                'text': 1,
                'rating': 1,
                'author.subscribers': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 0,
                'rating': {'result': 1},
                'tags.tag_name': 1
            }
        }
    ]

    # выполнение операции агрегации
    result = posts_collection.aggregate(pipeline)
    subs_posts = [post for post in result]
    count = posts_collection.aggregate([
        {
            "$lookup": {
                "from": "users",
                "localField": "author",
                "foreignField": "_id",
                "as": "author_doc"
            }
        },
        {
            "$match": {
                "author_doc.subscribers": current_user
            }
        },
        {
            "$count": "total_posts"
        }
    ])

    decoded_doc = [c for c in count]
    if len(decoded_doc) == 0:
        response = {'posts': [], 'count': 0}
    else:
        decoded_doc = decoded_doc[0]
        decoded_doc = decoded_doc['total_posts']
        print(f'decoded_doc - {decoded_doc}')
        response = {'posts': subs_posts, 'count': decoded_doc}
    return response
