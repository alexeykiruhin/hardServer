# получение постов
from flask import Blueprint, request
api_get_posts = Blueprint('api_get_posts', __name__)
# переменные из файла mongo.py
from mongo import posts_collection


@api_get_posts.route('/posts', methods=['GET', 'OPTIONS'])
def get_posts():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 2))

# добавить поле дата создания и тогда по ней можно сортироваться

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
                'text': 1,
                'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 0
            }
        }
    ]

    # выполнение операции агрегации
    result = posts_collection.aggregate(pipeline)
    # print(posts_collection.find({}))
    count = posts_collection.count_documents({})
    posts = [post for post in result]
    response = {'posts': posts, 'count': count}
    # response.set_cookie('test', 'test', samesite='None', secure=True)
    return response