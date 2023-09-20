# получение постов
from mongo import posts_collection
from flask import Blueprint, request, make_response

api_get_posts = Blueprint('api_get_posts', __name__)


# переменные из файла mongo.py


@api_get_posts.route('/posts', methods=['GET', 'OPTIONS'])
def get_posts():
    page = int(request.args.get('page'))
    page_size = int(request.args.get('page_size'))

    # добавить поле дата создания и тогда по ней можно сортироваться

    # операция агрегации
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
        # получаем теги поста
        {
            '$lookup': {
                'from': 'tags',
                'localField': 'tags',
                'foreignField': '_id',
                'as': 'tags'
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
                'subject': 1,
                'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author._id': 1,
                '_id': 1,
                'rating': {'result': 1},
                'tags.tag_name': 1
            }
        }
    ]

    # выполнение операции агрегации
    result = posts_collection.aggregate(pipeline)
    # print(posts_collection.find({}))
    count = posts_collection.count_documents({})
    posts = [post for post in result]
    for post in posts:
        post['id'] = str(post['_id'])
        del post['_id']
    for post in posts:
        # author, перобразование _id в строку
        if 'author' in post:
            post['author']['id'] = str(post['author']['_id'])
            del post['author']['_id']
    # posts['author._id'] = str(posts['author._id'])
    # response = {'posts': posts, 'count': count}
    # response.set_cookie('test', 'test', samesite='None', secure=True)
    # return response
    return posts
