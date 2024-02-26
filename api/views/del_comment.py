# удаление комментария
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
# переменные из файла mongo.py
from mongo import comments_collection
from bson import ObjectId

api_del_сomment = Blueprint('api_del_сomment', __name__)


@api_del_сomment.route('/del_comment', methods=['POST'])
@jwt_required()
def del_post():
    # получаем данные из запроса

    # добавить проверку токена, если юзер вышел то нужно запретить отправку нового статуса

    data = request.json
    print('del', data)
    comment_id = data['id']
    try:
        comments_collection.delete_one({'_id': ObjectId(comment_id)})
        response = {'status': True, 'id': comment_id}
    except:
        response = {'status': False, 'id': ''}
    return response
