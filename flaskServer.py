from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/posts": {"origins": "*"}})

posts = [
    {"id": 0, "nameUser": "user0", "textPost": "Textetxetetdteksdgd"},
    {"id": 1, "nameUser": "user1", "textPost": "Textetxetetdteksdgd"},
    {"id": 2, "nameUser": "user2", "textPost": "Textetasdasdxetetdteksdgd"},
    {"id": 3, "nameUser": "user3", "textPost": "Textetasdas123dteksdgd"},
    {"id": 4, "nameUser": "user4", "textPost": "Textetasdasdxetetdteksdgd"},
    {"id": 5, "nameUser": "user5", "textPost": "Textetxetetdteksdgd"},
]


@app.route('/posts', methods=['GET', 'OPTIONS'])
def get_posts():
    print(request.args.get('page'))
    page_number = int(request.args.get('page', 1))
    # бработка ошибки передачи параметра page=1
    if page_number == 0:
        page_number = 1
    page_size = 2
    start = (page_number - 1) * page_size
    end = start + page_size
    response = jsonify({'posts': posts[start:end], 'count': len(posts)})
    return response


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response


if __name__ == '__main__':
    app.run()
