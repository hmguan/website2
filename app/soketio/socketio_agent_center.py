from websocket.websocket_api import *
from threading import RLock
from flask import request
from pynsp.wait import *
import errtypes
import json

thread = None
thread_lock = RLock()
#线程等待消息队列
thread_msg_wait = waitable_handle(True)
is_exit_msg = False

post_msg_list=[]
post_room_list=[]

#key:client_id value:uuid
uuid_with_user_id = {}

def client_conneted(client_identify):
    print('WebSocket get a new client browser connected:{0},uuid_with_user_id:{1}'.format(client_identify,uuid_with_user_id))


def client_closed(client_identify):
    if thread_lock.acquire() == True:
        global uuid_with_user_id
        print('WebSocket end-close-uuid with user id:', uuid_with_user_id , ' and client identify:',client_identify)
        uuid_with_user_id.pop(client_identify)
        thread_lock.release()

def client_msg(msg_data,client_identify):
    try:
        json_data = json.loads(msg_data)
    except Exception as e:
        Logger().get_logger().error('WebSocket failed to convert str to json,please check it')
        return

    print('WebSocket get client message:', json_data)
    code=json_data['code']
    if code == errtypes.TypeShell_WebSokcetConnect:
        uuid_tmp = ''
        data = json_data.get('data')
        if data is not None:
            uuid_tmp = data.get('uuid')
        if thread_lock.acquire() == True:
            global uuid_with_user_id
            uuid_with_user_id[client_identify] = uuid_tmp
            thread_lock.release()
        print('WebSocket client message:',uuid_with_user_id)

def send_msg_to_client(uuid_value,msg):
    msg_dict = dict()
    msg_dict[uuid_value] = msg
    if thread_lock.acquire():
        global post_room_list
        post_room_list.append(msg_dict)
        thread_lock.release()

    global thread_msg_wait
    thread_msg_wait.sig()

def send_msg_to_all(msg):
    if thread_lock.acquire():
        global post_msg_list
        post_msg_list.append(msg)
        thread_lock.release()

    global thread_msg_wait
    thread_msg_wait.sig()

def post_msg_to_room(data,room_identify):
    send_msg_to_client(room_identify,data)
    print('room_identify',room_identify)

def background_thead():
    while True:
        global thread_msg_wait
        if (thread_msg_wait.wait(0xffffffff) == False):
            pass
        if is_exit_msg == True:
            break

        global post_msg_list,post_room_list
        while len(post_msg_list) != 0:
            if thread_lock.acquire():
                obj = post_msg_list.pop(0)
                thread_lock.release()
                message=''
                if type(obj) == type(dict()):
                    message = json.dumps(obj)
                else:
                    message = obj
                web_emit_all_client(message)
                print('WebSocket send message to all client session.')

        while len(post_room_list) != 0:
            if thread_lock.acquire():
                obj = post_room_list.pop(0)
                thread_lock.release()
                global uuid_with_user_id
                for key, item in obj.items():
                    if thread_lock.acquire():
                        client_items = {id_key:uuid_value for id_key,uuid_value in uuid_with_user_id.items() if uuid_value == key}
                        thread_lock.release()
                        message = ''
                        if type(item) == type(dict()):
                            message = json.dumps(item)
                        else:
                            message = item

                        print('**********************WebSocket client items:',client_items)
                        for user_id in client_items.keys():
                            web_emit_one_client(user_id,message)
                            print('WebSocket send message to client:',user_id)


def init_websocket(host,port):
    #创建监听
    web_listen(host,port)
    #注册链接回调
    regist_client_connected(client_conneted)
    #注册断开回调
    regist_client_closed(client_closed)
    #注册消息回调
    regist_client_message(client_msg)
    #创建发送消息队列线程
    global thread
    if thread is None:
        thread = threading.Thread(target=background_thead)
        thread.setDaemon(True)
        thread.start()