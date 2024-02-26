# получение постов
import bson
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, tags_collection
from flask import Blueprint, request

api_cp = Blueprint('api_cp', __name__)


# переменные из файла mongo.py


@api_cp.route('/cp', methods=['GET'])
@jwt_required()
def cp():
    current_user_id = get_jwt_identity()
    print('CP_data', current_user_id)
    if current_user_id != '65ca149a996b4b483291c402':
        return {'access': False}



    # tags = tags_collection.find({}, {'tag_name': 1, '_id': 0})
    # tags = [tag['tag_name'] for tag in tags]
    print(f'cp')
    return 'cp'
