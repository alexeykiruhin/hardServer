from flask import Flask
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


@app.route('/')
def getusers():  # put application's code
    users_list = [{'id': 1, 'name': 'PLayer1'}, {'id': 2, 'name': 'PLayer2'}]
    users = {'users': users_list, 'totalCount': len(users_list)}
    msg_json = json.dumps(users)
    return msg_json


if __name__ == '__main__':
    app.run()
