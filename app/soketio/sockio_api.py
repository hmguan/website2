from app import local_socketio
from flask import request
from flask_socketio import SocketIO, emit,join_room,leave_room
import json
import errtypes
from pynsp.logger import *

def response_to_client_data(data):
    print('------------------send message to clien:',data)
    local_socketio.emit('server_response',data,
                        namespace='/notify_call')

def send_messge_to_room(data,room_identify):
    local_socketio.emit('room_response',{'data': data},namespace='/notify_call',
                        room_identify=room_identify,broadcast=True)

def close_room(room_identify):
    local_socketio.close_room(room_identify,namespace='/notify_call')

def broadcast_message(message):
    local_socketio.emit('server_response',{'data':message},broadcast=True)

@local_socketio.on('connect', namespace='/notify_call')
def socketio_connect():
    print('----------------socketio connected------------------')
    response_to_client_data({'msg_type':errtypes.TypeShell_SokcetIOConnect,'data':'connect success'})

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

