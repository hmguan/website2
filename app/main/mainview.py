import flask
from flask import jsonify
from flask import Flask,render_template,request, session
from werkzeug.utils import secure_filename
import uuid
import json
from pynsp.logger import *
from . import main
import errtypes

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
        login_id = json_data.get('login_id')
        if login_id is None or type(login_id) != type(int):
            return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament })


        event = json_data.get('event')
    except Exception as e:
        return jsonify({'code':errtypes.HttpResponseCode_ServerError,'msg': str(e)})

    if event in map_event_obj.keys():
        obj = map_event_obj[event]
        return obj.flask_recvdata(request)
    print('can not find event:', event)
    return jsonify({'code':errtypes.HttpResponseCode_InvaildEvent,'msg': errtypes.HttpResponseMsg_InvaildEvent})

def query_event(data):
    print('data', data)
    json_data = json.loads(data.decode('utf-8'))
    event = json_data['event']

    if event in map_event_obj.keys():
        obj = map_event_obj.get(event)
        if obj is not None:
            return obj.flask_recvdata(request)
        else:
            print('the function object of event:{0} is null'.format(event))

    return jsonify({'code': errtypes.HttpResponseCode_InvaildEvent, 'msg': errtypes.HttpResponseMsg_InvaildEvent})

@main.route('/login',methods=["GET","POST"])
def login():
    print('login route method:',request.method)
    return query_event(request.get_data())

@main.route('/logger',methods=['GET','POST'])
def write_log():
    print('logger route method:',request.method)
    return query_event(request.get_data())
    # data = request.get_data()
    # print('data',data)
    # json_data = json.loads(data.decode('utf-8'))
    # event = json_data['event']
    #
    # if event in map_event_obj.keys():
    #     obj = map_event_obj.get(event)
    #     if obj is not None:
    #         return obj.flask_recvdata(request)
    #     else:
    #         print('the function object of event:{0} is null'.format(event))
    #
    # return jsonify({'code': errtypes.HttpResponseCode_InvaildEvent, 'msg': errtypes.HttpResponseMsg_InvaildEvent})

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