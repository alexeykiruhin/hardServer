# получение постов
import bson
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongo import posts_collection, tags_collection
from flask import Blueprint, request
api_search = Blueprint('api_search', __name__)
# переменные из файла mongo.py



@api_search.route('/search', methods=['POST'])
@jwt_required()
def search():
    data = request.json
    tag = data['tag']
    print(f'tags - {tag}')

    tagId = tags_collection.find({'tag_name': tag}, {'tag_name': 0})
    tagId = [i['_id'] for i in tagId]
    print(f'tagId - {tagId}')
    out = posts_collection.find({'tags': {"$in": [tagId[0]]}},{'text': 1, '_id': 0, 'id': 1})
    out = [{'text': o['text'], 'id': o['id']} for o in out]
    
    print(f'result - {out}')
    response = {'result': out}
    return response