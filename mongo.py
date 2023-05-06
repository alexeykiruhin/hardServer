from pymongo import MongoClient

# создаем подключение к MongoDB
client = MongoClient('mongodb://localhost:27017/')

# выбираем базу данных
db = client['content_site']

# выбираем коллекцию пользователей
users_collection = db['users']

# выбираем коллекцию постов
posts_collection = db['posts']

# выбираем коллекцию комментариев
comments_collection = db['comments']