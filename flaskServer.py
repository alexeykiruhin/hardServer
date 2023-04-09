from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import mongo

# переменные из файла mongo.py
users_collection = mongo.users
posts_collection = mongo.posts

app = Flask(__name__)
CORS(app, resources={r"/posts": {"origins": "*"}})
app.secret_key = 'secret'


# инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# реализация класса пользователя
class User(UserMixin):
    def __init__(self, id, username, password, img):
        self.id = id
        self.username = username
        self.img = img
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def get_info(self):
        return {'username': self.username, 'img': self.img}


# реализация функции для получения пользователя по его id
@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = int(user_id)
    return user


# обработка запроса на регистрацию пользователя !не доделана
@app.route('/register', methods=['POST'])
def register():
    # получаем данные из запроса
    data = request.json

    # проверяем, что такой пользователь не существует
    user = users_collection.find_one({'username': data['username']}, {'_id': 0})
    if user:
        # существует
        return jsonify({'error': 'User already exists'})
    else:
        # создаем нового пользователя
        if data['username'] and data['password']:
            #  проверяем что логин и пароль передали
            pass
            return jsonify({'message': 'User registered successfully'})
        else:
            return jsonify({'error': 'Missing username or password'})


# обработка запроса на авторизацию пользователя
@app.route('/login', methods=['POST'])
def login():
    # получаем данные из запроса
    data = request.json
    # ищем пользователя в базе данных
    user = users_collection.find_one({'username': data['username']}, {'_id': 0})
    # проверяем пароль
    if user['password'] == data['password']:
        # создаем токен
        # token = create_access_token(identity=user['id'])
        # кастылём удаляю пароль из ответа
        del user['password']
        # возвращаем токен
        # return jsonify({'access_token': token})
        return jsonify({'user_obj': user, 'isAuth': True})

    # возвращаем ошибку
    return jsonify({'message': 'Invalid username or password'}), 401


# обработка запроса на выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'User logged out successfully'})


# защита эндпоинта для авторизованных пользователей
@app.route('/protected')
@login_required
def protected():
    return jsonify({'message': 'You are authorized!'})


# получение постов
@app.route('/posts', methods=['GET', 'OPTIONS'])
def get_posts():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 2))

    # операция агрегации
    pipeline = [
        # поиск всех постов с информацией об авторе
        {
            '$lookup': {
                'from': 'users',
                'localField': 'author',
                'foreignField': '_id',
                'as': 'author'
            }
        },
        # объединение данных о посте и авторе
        {
            '$unwind': '$author'
        },
        # сортировка по дате создания в порядке убывания
        {
            '$sort': {
                'created_at': -1
            }
        },
        # пропуск документов для реализации пагинации
        {
            '$skip': (page - 1) * page_size
        },
        # ограничение количества выдаваемых документов
        {
            '$limit': page_size
        },
        # исключение поля "_id" из документа автора
        {
            '$project': {
                'text': 1,
                'rating': 1,
                'author.username': 1,
                'author.img': 1,
                'author.id': 1,
                '_id': 0
            }
        }
    ]

    # выполнение операции агрегации
    result = posts_collection.aggregate(pipeline)
    count = posts_collection.count_documents({})
    posts = [post for post in result]
    return jsonify({'posts': posts, 'count': count})


# добавление поста
@app.route('/posts', methods=['POST'])
def add_post():
    post_data = request.json
    author_id = post_data['author_id']
    post_text = post_data['text']

    # получаем автора поста из коллекции users
    author = users_collection.find_one({'_id': author_id})

    # создаем новый документ в коллекции posts
    new_post = {
        'text': post_text,
        'author': {
            '_id': author['_id'],
            'username': author['username']
        }
    }
    result = posts_collection.insert_one(new_post)

    # возвращаем id добавленного поста
    return jsonify({'id': str(result.inserted_id)})


@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    users_list = []
    for user in users_collection.find({}, {'_id': 0, 'password': 0}):
        users_list.append(user)
    count = users_collection.count_documents({})
    response = jsonify({'users': users_list, 'count': count})
    return response


@app.route('/user/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_user(user_id):
    user_info = users_collection.find_one({'id': user_id}, {'_id': 0, 'password': 0})
    user_posts = posts_collection.aggregate([
        {
            '$lookup':
                {
                    'from': "users",
                    'localField': "author",
                    'foreignField': "_id",
                    'as': "author_info"
                }
        },
        {
            '$match': {
                "author_info.id": user_id
            }
        },
        # исключение полей
        {
            '$project': {
                'text': 1,
                # 'rating': 1,
                '_id': 0
            }
        }
    ])
    # создаём список из объекта бд
    user_posts = list(user_posts)
    # вычисляем и записываем количество постов в информацию о юзере
    user_info['posts_count'] = len(user_posts)
    # преобразовываем объект бд в список постов
    user_posts = [txt['text'] for txt in user_posts]
    response = jsonify({'user_info': user_info, 'user_posts': user_posts})

    return response


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response


if __name__ == '__main__':
    app.run()
