import datetime
import re

from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, users_collection, tags_collection  # переменные из файла mongo.py

api_add_post = Blueprint('api_add_post', __name__)


@api_add_post.route('/posts', methods=['POST'])
@jwt_required()
def add_post():
    """Добавление поста
    post_data - {'title': 'name', 'text': 'text', 'file': '', 'tags': 'tag,sd,s'}
    """
    author_id = get_jwt_identity()  # айди юзера из куки

    post_data = request.json  # данные из запроса

    # Разделители, которые вы хотите использовать
    delimiters = [',', ' ', ';', '-', '#', ', ', ' ',]

    # Разделите строку на массив, используя разные разделители
    # dtags = re.split('|'.join(map(re.escape, delimiters)), post_data["post_data"]["tags"])  # список тегов

    # Разбиваем строку и удаляем пустые строки
    dtags = list(filter(None, re.split('|'.join(map(re.escape, delimiters)), post_data["post_data"]["tags"])))

    # dtags = post_data["post_data"]["tags"].split(', ')  # список тегов старая версия

    date = datetime.datetime.now()# дата для добавление в информацию о посте

    print(f'date - {date}')

    # post_text = post_data['text']
    # post_tags = post_data['tags']
    print(f'tags - {dtags}')
    # получаем автора поста из коллекции users
    # author = users_collection.find_one({'_id': ObjectId(author_id)}, {'_id': 1})
    print(f'author - {ObjectId(author_id)}')

    # добавляем теги в бд
    out_tags = []
    for t in dtags:
        # проверяем есть ли такой тег
        find_tag = tags_collection.find_one({"tag_name": t}, {"_id": 1})

        if find_tag is None:
            new_tag = tags_collection.insert_one({"tag_name": t})
            out_tags.append(new_tag.inserted_id)
            print("Документ не найден.")
        else:
            tag_id = find_tag["_id"]
            out_tags.append(tag_id)
            print("Обновленный документ:", find_tag["_id"])

    print(out_tags)

    # создаем новый документ в коллекции posts
    new_post = {
        "subject": post_data["post_data"]["title"],
        "text": post_data["post_data"]["text"],
        "rating": {
            "result": 0,
            "usersRated": []
        },
        "author": ObjectId(author_id),
        "tags": out_tags,
        "img": post_data["post_data"]["file"],
        "date": date
    }
    # # добавляем пост в бд
    # posts_collection.insert_one(new_post)
    post = posts_collection.insert_one(new_post)
    print(post.inserted_id)

    # нужно переделать создание поста так что бы созданный или найденный тег добавлялся в коллекцию постс в новый пост,
    # что бы пост знал какие у него теги а не тег какие у него посты

    # возвращаем флаг создания поста
    return {'isCreate': True}
