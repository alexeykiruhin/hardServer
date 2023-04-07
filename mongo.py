from pymongo import MongoClient

# создаем подключение к MongoDB
client = MongoClient('mongodb://localhost:27017/')

# выбираем базу данных
db = client['content_site']

# выбираем коллекцию пользователей
users = db['users']

# выбираем коллекцию постов
posts = db['posts']
