import flask
from flask import jsonify
from flask import Flask,render_template,request, session
from werkzeug.utils import secure_filename
import uuid
import json
from pynsp.logger import *
from . import main
import errtypes
from ..user.user_service_agant import users_center


#the dict save the relationship route with event,
#{event:object}
map_event_obj = {}

@main.route('/', methods=["GET",'POST'])
def index():
    print('main route method:',request.method)
    if 'GET' == request.method:
        uid_value = uuid.uuid4()

        resp= flask.make_response(render_template('index.html'))
        resp.set_cookie('token',str(uid_value).encode('utf-8'))
        return resp
    try:
        data = request.get_data()
        print('data:',data)
        json_data = json.loads(data.decode('utf-8'))
        login_token = json_data.get('login_token')

        if login_token is None or type(login_token) != str:
            return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament })

        (retval,user_id) = users_center.check_user_login(login_token)
        if retval!=0:
            return jsonify({'code': errtypes.HttpResponseCode_InvaildToken,'msg': errtypes.HttpResponseCodeMsg_InvaildToken })

        event = json_data.get('event')
        json_data['login_id']=user_id

    except Exception as e:
        return jsonify({'code':errtypes.HttpResponseCode_ServerError,'msg': str(e)})

    if event in map_event_obj.keys():
        obj = map_event_obj[event]
        return obj.flask_recvdata(json_data)
    print('can not find event:', event)
    return jsonify({'code':errtypes.HttpResponseCode_InvaildEvent,'msg': errtypes.HttpResponseMsg_InvaildEvent})

def query_event(request_data,event_name):
    try:
        json_data = json.loads(request_data.decode('utf-8'))
        obj = map_event_obj.get(event_name)
        if event_name != json_data.get('event') or obj is None:
            return jsonify({'code':errtypes.HttpResponseCode_InvaildEvent,'msg': errtypes.HttpResponseMsg_InvaildEvent})
        return obj.flask_recvdata(json_data)
    except Exception as e:
        return jsonify({'code':errtypes.HttpResponseCode_ServerError,'msg': str(e)})

@main.route('/login',methods=["GET","POST"])
def login():
    print('login route method:',request.method)
    return query_event(request.get_data(),'event_login')

@main.route('/logger',methods=['GET','POST'])
def write_log():
    print('logger route method:',request.method)
    return query_event(request.get_data(),'write_logger_event')

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