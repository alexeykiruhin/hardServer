from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/posts": {"origins": "*"}})
app.secret_key = 'secret'

# имитация базы данных пользователей
users = {
    1: {'id': 1, 'username': 'Alice', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/women/69.jpg'},
    2: {'id': 2, 'username': 'Dave', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/women/74.jpg'},
    3: {'id': 3, 'username': 'Bob', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/11.jpg'},
    4: {'id': 4, 'username': 'Ivan', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/women/55.jpg'},
    5: {'id': 5, 'username': 'user5', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/women/20.jpg'},
    6: {'id': 6, 'username': 'user6', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/women/84.jpg'},
    7: {'id': 7, 'username': 'user7', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/84.jpg'},
    8: {'id': 8, 'username': 'user8', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/8.jpg'},
    9: {'id': 9, 'username': 'user9', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/17.jpg'},
    10: {'id': 10, 'username': 'user10', 'password': 'password1',
     'img': 'https://randomuser.me/api/portraits/women/84.jpg'},
    11: {'id': 11, 'username': 'user11', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/31.jpg'},
    12: {'id': 12, 'username': 'user12', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/93.jpg'},
    13: {'id': 13, 'username': 'user13', 'password': 'password1',
     'img': 'https://randomuser.me/api/portraits/women/92.jpg'},
    14: {'id': 14, 'username': 'user14', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/61.jpg'},
    15: {'id': 15, 'username': 'user15', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/11.jpg'},
    16: {'id': 16, 'username': 'user16', 'password': 'password1',
     'img': 'https://randomuser.me/api/portraits/women/18.jpg'},
    17: {'id': 17, 'username': 'user17', 'password': 'password1',
     'img': 'https://randomuser.me/api/portraits/women/25.jpg'},
    18: {'id': 18, 'username': 'user18', 'password': 'password1',
     'img': 'https://randomuser.me/api/portraits/women/77.jpg'},
    19: {'id': 19, 'username': 'user19', 'password': 'password1', 'img': 'https://randomuser.me/api/portraits/men/89.jpg'},
    20: {'id': 20, 'username': 'user20', 'password': 'password1',
     'img': 'https://randomuser.me/api/portraits/women/98.jpg'}
}

posts = [
    {"id": 1, "userId": users[1]['id'], "nameUser": "Alice",
     "textPost": "Интересные у тебя татуировки на ногах. Что они означают? Это варикоз."},
    {"id": 2, "userId": users[2]['id'], "nameUser": "Dave",
     "textPost": "Сегодня я настолько ленив, что мои сны уже имеют субтитры."},
    {"id": 3, "userId": users[3]['id'], "nameUser": "Bob",
     "textPost": "Если ты думаешь, что никогда не совершал глупых поступков, то ты просто не обращал на них внимания."},
    {"id": 4, "userId": users[4]['id'], "nameUser": "Ivan",
     "textPost": "Женщины не стареют, они просто переходят на другой уровень!"},
    {"id": 5, "userId": users[5]['id'], "nameUser": "user5",
     "textPost": "Если ты думаешь, что всё уже позади, то скорее всего ты идёшь задом наперёд."},
    {"id": 6, "userId": users[6]['id'], "nameUser": "Bob",
     "textPost": "Если бы я был денежным знаком, то я был бы знаком вопросительным, потому что жизнь полна неожиданных поворотов."},
    {"id": 7, "userId": users[7]['id'], "nameUser": "Julia",
     "textPost": "Я не ленивый, я просто экономлю энергию на важные вещи."},
    {"id": 8, "userId": users[8]['id'], "nameUser": "Dave",
     "textPost": "Все люди делятся на две категории: те, кто могут делать математические вычисления, и те, кто не могут."},
    {"id": 9, "userId": users[9]['id'], "nameUser": "user9",
     "textPost": "Будущее близко, но в прошлое можно вернуться с помощью гугла."},
    {"id": 10, "userId": users[10]['id'], "nameUser": "user10",
     "textPost": "Я не знаю, какие планы на сегодня у других, но у меня есть важное свидание с моей постелью."},
    {"id": 11, "userId": users[11]['id'], "nameUser": "user11",
     "textPost": "Мне кажется, что кто-то где-то смотрит на меня и думает: «Ну вот идиот…»."},
]

# инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# users = {
#     1: {'id': 1, 'username': 'user1', 'password': 'password1'},
#     2: {'id': 2, 'username': 'user2', 'password': 'password2'},
#     3: {'id': 3, 'username': 'user3', 'password': 'password3'}
# }


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


# обработка запроса на регистрацию пользователя
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if username and password:
        # проверяем, что такой пользователь не существует
        for user in users.values():
            if user['username'] == username:
                return jsonify({'error': 'User already exists'})

        # создаем нового пользователя
        user_id = max(users.keys()) + 1
        users[user_id] = {'id': user_id, 'username': username, 'password': password}
        return jsonify({'message': 'User registered successfully'})
    else:
        return jsonify({'error': 'Missing username or password'})


# обработка запроса на авторизацию пользователя
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'})

    # проверяем, что пользователь существует и введенный пароль верный
    for user in users.values():
        if user['username'] == username and user['password'] == password:
            id = user['id']
            username = user['username']
            img = user['img']
            password = user['password']
            user_obj = User(id, username, password, img)
            login_user(user_obj)
            print(user_obj.get_info())
            # login: 0 ошибок нет
            return jsonify({'user_obj': user_obj.get_info(), 'isAuth': user_obj.is_authenticated()})

    return jsonify({'error': 'Invalid username or password'})


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


@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    users_list = list(users.values())
    response = jsonify({'users': users_list, 'count': len(users)})
    print(response)
    return response


@app.route('/user/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_user(user_id):
    users_list = list(users.values())
    response = jsonify({'user': users_list[user_id - 1]})
    print(response)
    return response


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response


if __name__ == '__main__':
    app.run()
