from websocket.websocket_server import *

def web_listen(host='0.0.0.0',port=5510):
    '''
    start websocket server listen by create a new thread
    for server
    :param host: string value
    :param port: int value
    :return:
    '''
    server = websocket_server(host,port)
    server.start()

def web_emit_all_client(msg):
    '''
    webscoket server send message to all client browser
    :param msg:string value of message
    :return:
    '''
    notify_all_client(msg)

def web_emit_one_client(client_identify,msg):
    '''
    websocket server send message to client browser by client user_id
    :param client_identify:string value
    :param msg:string value
    :return:
    '''
    notify_one_client(client_identify, msg)

def regist_client_connected(notify_callback):
    '''
    notify the callback function the client address id
    :param notify_callback:the callback parament is string of id address
    e.g:notify_callback('11234')
    :return:
    '''
    regist_connect_callback(notify_callback)

def regist_client_closed(notify_callback):
    '''
    notify the callback function the browser client is closed
    :param notify_callback: the callback parament is string of id address
    e.g:notify_callback('11234')
    :return:
    '''
    regist_close_callback(notify_callback)

def regist_client_message(notify_callback):
    '''
    notify the callback function for the browser client message
    :param notify_callback: the callback parament is string of message
    e.g:notify_callback('this is test message','12345')
    :return:
    '''
    regist_recvdata_callback(notify_callback)

def close_websocket(client_identify):
    '''
    close the client session with webserver
    :param client_identify:
    :return:
    '''
    close_client_websocket(client_identify)
