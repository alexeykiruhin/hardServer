# получение постов
import bson
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, tags_collection
from flask import Blueprint, request

api_get_tags = Blueprint('api_get_tags', __name__)


# переменные из файла mongo.py


@api_get_tags.route('/get_tags', methods=['GET'])
@jwt_required()
def search():

    tags = tags_collection.find({}, {'tag_name': 1, '_id': 0})
    tags = [tag['tag_name'] for tag in tags]
    print(f'tags - {tags}')
    return tags
