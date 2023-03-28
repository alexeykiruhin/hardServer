from flask import Flask
import json
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code
    list = {{'id': 1, 'name': 'PLayer1'}, {'id': 2, 'name': 'PLayer2'}}
    msg_json = json.dumps(list)
    return msg_json



if __name__ == '__main__':
    app.run()
