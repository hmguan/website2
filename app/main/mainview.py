import flask
from flask import jsonify
from flask import Flask,render_template,request, session
from werkzeug.utils import secure_filename
import uuid
import json
from pynsp.logger import *
from . import main
import errtypes

# from db.db_users import user
# from configuration import config
# from db.db_package import package_manager

#the dict save the relationship route with event,
#{event:object}
map_event_obj = {}

@main.route('/', methods=["GET",'POST'])
def index():
    print('main route method:',request.method)
    if 'GET' == request.method:
        uid_value = uuid.uuid4()
        # flask.session['uid']=uid_value

        resp= flask.make_response(render_template('index.html'))
        resp.set_cookie('token',str(uid_value).encode('utf-8'))
        print('--------------uid:',uuid.uuid4())
        return resp
    # try:
    data = request.get_data()
    print('data:',data)
    json_data = json.loads(data.decode('utf-8'))
    event = json_data['event']
    print(event)

    if event in map_event_obj.keys():
        obj = map_event_obj[event]
        return obj.flask_recvdata(request)
    print('can not find event:', event)
    return jsonify({'code':errtypes.HttpResponseCode_InvaildEvent,'msg':''})

@main.route('/test')
def test():
    return render_template('test.html')

class base_event():
    def __init__(self):
        pass

    def __del__(self):
        pass

    def regist_event(self,*args):
        if len(args) == 0:
            Logger().get_logger().warning('can not regist any event,the event vaflue is empty.')
            return
        for index,element in enumerate(args):
            if element in map_event_obj.keys():
                Logger().get_logger().warning('the event:{0} has already registe,please check it.'.format(element))
                continue
            map_event_obj[element] = self
        pass

    def flask_recvdata(self,requst_obj):
        '''
        virtual function for flask reqeust handler,
        the child class must override this function
        '''
        pass