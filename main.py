import os
from pprint import pprint

from flask import Flask, request
import json
from voice import Voice

dir_prog = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_prog)

app = Flask(__name__)
app.debug = True
dc_obj_voice = {}

@app.route('/', methods=['GET', 'POST'])
def start():
    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }
    session_id = request.json['session']["session_id"]
    if request.json['session']['new']:
        # Создание экземпляра класса Voice()
        obj_voice = Voice()
        dc_obj_voice[session_id] = obj_voice
        response["response"]["text"] = obj_voice.hello()
        response["session_state"] = {'def_name': 'get_lsh'}
    else:
        obj_voice = dc_obj_voice[session_id]
        dc_resp = obj_voice.routerResp(request)
        pprint(request.json)
        response["response"]["text"] = dc_resp['text_resp']
        response["session_state"] = {'def_name': dc_resp['def_name']}
    return json.dumps(response)


if __name__ == '__main__':
    context = (dir_prog + os.sep + r'/archive/yandexskill.ru/fullchain1.pem',
               dir_prog + os.sep + r'/archive/yandexskill.ru/privkey1.pem')
    app.run(host='192.168.1.2', port=5000, ssl_context=context, threaded=True, debug=True)