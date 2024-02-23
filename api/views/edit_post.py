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
    print('edit_post', post)
    # new_post_text = data['text']
    # добавляем теги в бд
    out_tags = []
    rec_tags = []
    for tag in post["tags"]:
        # проверяем есть ли такой тег
        find_tag = tags_collection.find_one({"tag_name": tag}, {"tag_name": 1, '_id': 1})

        if find_tag is None:
            new_tag = tags_collection.insert_one({"tag_name": tag})
            rec_tags.append(new_tag.inserted_id)
            out_tags.append({"tag_name": tag})
            print("Документ не найден.")
        else:
            rec_tags.append(find_tag["_id"])
            out_tags.append({"tag_name": find_tag['tag_name']})
            print("Обновленный документ:", find_tag["_id"])
    print('tegi ', out_tags)

    try:  # не находит
        print('id - ', post['id'])
        print('post["text"]', post["text"])
        print('post["subject"]', post["subject"])
        print('post["file"]', post["img"])

        print(posts_collection.find_one({'_id': ObjectId(post["id"])}))
        result = posts_collection.update_one({'_id': ObjectId(post["id"])}, {
            '$set': {'text': post["text"], 'subject': post["subject"], 'tags': rec_tags, 'img': post["img"]}})
        print('result', result.modified_count)
        if result.modified_count == 1:
            print('HAHA')
            # response = posts_collection.find_one({'_id': ObjectId(post["id"])})
            # response['id'] = post["id"]
            # del response['_id']
            # response['author']['id'] = str(response['author']['_id'])
            # del response['author']['_id']
            post['tags'] = out_tags
            response = post
            print('response', response)
        else:
            print(1)
            response = {'editPost': False}
    except:
        print(2)
        response = {'editPost': False}
    return response
