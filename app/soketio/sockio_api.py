from app import local_socketio
from flask import request
from flask_socketio import SocketIO, emit,join_room,leave_room
import json
import errtypes
from pynsp.logger import *

from threading import RLock

thread = None
thread_lock = RLock()

post_msg_list=[]
post_room_list=[]

def response_to_client_data(data):
    print('------------------send message to clien:',data)
    post_msg_list.append(data)

def send_messge_to_room(data,room_identify):
    # local_socketio.emit('room_response',{'data': data},namespace='/notify_call',
    #                     room_identify=room_identify,broadcast=True)
    msg_dict=dict()
    msg_dict[room_identify] = data
    post_room_list.append(msg_dict)

def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        local_socketio.sleep(1)
        while len(post_msg_list) != 0:
            obj = post_msg_list.pop(0)
            print('----------obj:',obj)
            local_socketio.emit('server_response',obj,
                                namespace='/notify_call')

        while len(post_room_list) != 0:
            obj = post_room_list.pop(0)
            for key,item in obj.items():
                local_socketio.emit('room_response',{'data': item},namespace='/notify_call',
                                    room_identify=key,broadcast=True)

@local_socketio.on('connect', namespace='/notify_call')
def socketio_connect():
    print('----------------socketio connected------------------')
    global thread
    with thread_lock:
        if thread is None:
            thread = local_socketio.start_background_task(target=background_thread)
    response_to_client_data({'msg_type':errtypes.TypeShell_SokcetIOConnect,'data':'connect success'})

    print('--------------connected successfully---------------')

@local_socketio.on('disconnect', namespace='/notify_call')
def socketio_disconnect():
    print('----------------socketio disconnect------------------')
    print('sid:%s '%(request.sid))

@local_socketio.on('join', namespace='/notify_call')
def socketio_join(room_identify):
    print('-------------join room:',room_identify['uuid'])
    join_room(room_identify['uuid'])

@local_socketio.on('leave', namespace='/notify_call')
def socketio_leave(room_identify):
    print('-------------leave room:',room_identify['uuid'])
    leave_room(room_identify['uuid'])

@local_socketio.on('client_ping', namespace='/notify_call')
def ping_pong():
    Logger().get_logger().info('client send ping message.')
    pass

