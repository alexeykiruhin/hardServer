from flask import Flask, jsonify

app = Flask(__name__)

posts = [
    {"id": 1, "nameUser": "user1", "textPost": "Textetxetetdteksdgd"},
    {"id": 2, "nameUser": "user2", "textPost": "Textetasdasdxetetdteksdgd"},
    {"id": 3, "nameUser": "user3", "textPost": "Textetasdas123dteksdgd"},
    {"id": 4, "nameUser": "user4", "textPost": "Textetasdasdxetetdteksdgd"},
    {"id": 5, "nameUser": "user5", "textPost": "Textetxetetdteksdgd"},
]


@app.route('/posts/<int:start>')
def get_posts(start):
    end = start + 2
    response = jsonify({'posts': posts[start:end]})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run()
