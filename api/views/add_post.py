# добавление поста
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
api_add_post = Blueprint('api_add_post', __name__)
# переменные из файла mongo.py
from mongo import posts_collection, users_collection, tags_collection


@api_add_post.route('/posts', methods=['POST'])
@jwt_required()
def add_post():
    author_id = get_jwt_identity()  # айди юзера из куки
    post_data = request.json
    post_text = post_data['text']
    post_tags = post_data['tags']
    print(f'post_tags - {post_tags}')
    # получаем автора поста из коллекции users
    author = users_collection.find_one({'id': author_id}, {'_id': 1})

    out_tags = []
    # добавляем теги в бд
    for t in post_tags:
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
        "text": post_text,
        "rating": {
            "result": 0,
            "usersRated": []
        },
        "author": author['_id'],
        "tags": out_tags
    }
    # добавляем пост в бд
    # posts_collection.insert_one(new_post)
    post = posts_collection.insert_one(new_post)
    # print(post.inserted_id)

    # нужно переделать создание поста так что бы созданный или найденный тег добавлялся в коллекцию постс в новый пост, что бы пост знал какие у него теги а не тег какие у него посты    

    
    # возвращаем флаг создания поста
    return {'isCreate': True}
