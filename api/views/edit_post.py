# получение постов
from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
# переменные из файла mongo.py
from mongo import posts_collection, tags_collection

api_edit_post = Blueprint('api_edit_post', __name__)


@api_edit_post.route('/edit_post', methods=['POST'])
@jwt_required()
def edit_post():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    post = data['post_data']
    # new_post_text = data['text']
    # добавляем теги в бд
    out_tags = []
    for tag in post["tags"]:
        # проверяем есть ли такой тег
        find_tag = tags_collection.find_one({"tag_name": tag}, {"_id": 1})

        if find_tag is None:
            new_tag = tags_collection.insert_one({"tag_name": tag})
            out_tags.append(new_tag.inserted_id)
            print("Документ не найден.")
        else:
            tag_id = find_tag["_id"]
            out_tags.append(tag_id)
            print("Обновленный документ:", find_tag["_id"])

    print(out_tags)

    print(f'post - {post}')
    try:
        posts_collection.update_one({'_id': ObjectId(post["id"])}, {
            '$set': {'text': post["text"], 'subject': post["title"], 'tags': out_tags, 'img': post["file"]}})
        response = post
    except:
        response = {'editPost': False}
    return response
