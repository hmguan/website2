import websocket.websocket_type as ws_type
from time import sleep
import threading
import socket
import hashlib
import base64
import struct
from threading import RLock
from pynsp.logger import *

clients={}
client_lock = RLock()

connected_notify_callback=None
closed_notify_callback=None
recvdata_notify_callback=None

def encode_webmessage(type,message):
    data = struct.pack('B', type)

    msg_len = len(message)
    if msg_len <= 125:
        data += struct.pack('B', msg_len)
    elif msg_len <= (2 ** 16 - 1):
        data += struct.pack('!BH', 126, msg_len)
    elif msg_len <= (2 ** 64 - 1):
        data += struct.pack('!BQ', 127, msg_len)
    else:
        Logger().get_logger().warning('WebSocket message is to long')
        return ''
    data += bytes(message, encoding='utf-8')
    return data

def notify_all_client(msg):
    data = encode_webmessage(0x80 | ws_type.WS_TEXT_FRAME,msg)
    if len(data) == 0:
        Logger().get_logger().warning('WebSocket can not send message to any client,beacuse the message is null')
        return

    global clients,client_lock
    key_item = list(clients.keys())
    for item in key_item:
        Logger().get_logger().info('WebSocket send message to client:{0}'.format(item))
        try:
            if client_lock.acquire():
                if clients.get(item) is not None:
                    result = clients.get(item).send(data)
                client_lock.release()
                Logger().get_logger().info('WebSocket send message to client:{0} and msg:{1} successfully.'.format(item,msg))
        except Exception as e:
            Logger().get_logger().error('WebSocket server get error while send to client:{0}, and error message:{1}'.format(item ,str(e)))
            if client_lock.acquire():
                clients.get(item).close()
                clients.pop(item)
                client_lock.release()

def notify_one_client(identify,msg):
    global clients,client_lock
    if identify not in clients.keys():
        Logger().get_logger().warning('WebSocket can not find identify:{0} in the all client collection.'.format(identify))
        return
    data = encode_webmessage(0x80 | ws_type.WS_TEXT_FRAME,msg)
    if len(data) == 0:
        Logger().get_logger().warning('WebSocket can not send message to target client,beacuse the message is null')
        return

    if client_lock.acquire():
        client_session = clients.get(identify)
        client_lock.release()
        try:
            if client_session is not None:
                client_session.send(data)
                Logger().get_logger().info('WebSocket send message to one single client:{0} and msg:{1} successfully.'.format(identify,msg))
            else:
                Logger().get_logger().error('WebSocket client session:{0} is null,then can not send message.'.format(identify))
        except Exception as e:
            Logger().get_logger().error('WebSocket server get error:{0}'.format(str(e)))
            client_session.close()
            if client_lock.acquire():
                if identify in clients.keys():
                    clients.pop(identify)
                client_lock.release()

def regist_connect_callback(notify_callback):
    global connected_notify_callback
    connected_notify_callback = notify_callback

def regist_close_callback(notify_callback):
    global closed_notify_callback
    closed_notify_callback=notify_callback

def regist_recvdata_callback(notify_callback):
    global recvdata_notify_callback
    recvdata_notify_callback = notify_callback

def close_client_websocket(client_identify):
    global clients,client_lock
    if client_lock.acquire() == True:
        connection = clients.get(client_identify)
        if connection is not None:
            try:
                connection.send(encode_webmessage(0x80 | ws_type.WS_CLOSEF_FRAME,ws_type.WS_CLOSE_NORMAL))
            except Exception as e:
                Logger().get_logger().error('WebSocket get error while close client websocket:{0}'.format(str(e)))
        client_lock.release()

#########################################################################################

class websocket_thread(threading.Thread):
    def __init__(self,connection,userid):
        super(websocket_thread,self).__init__()
        self.__connection=connection
        self.__userid=userid

    def __del__(self):
        Logger().get_logger().info('WebSocket client destory __del__.')

    def parse_headers(self,msg):
        #print('head data',msg)
        headers = {}
        header,data =msg.split(b'\r\n\r\n',1)
        for line in header.split(b'\r\n')[1:]:
            key,value=line.split(b':',1)
            headers[key.decode('utf-8')]=value.decode('utf-8').strip()
        headers['data']=data
        return headers

    def parse_data(self,msg):
        if len(msg) == 0:
            Logger().get_logger().warning('WebSocket get the message is null,then can not parse WebSocket data')
            return '',0
        # print('recv data:',msg)
        opcode=msg[0] & 0x0f
        is_mask = (msg[1] & 0x80) >> 7
        print('opcode:',opcode)
        msg_len = msg[1] & 0x7F
        if msg_len == 0x7E:
            mask = msg[4:8]
            content = msg [8:]
        elif msg_len == 0x7F:
            mask=msg[10:14]
            content=msg[14:]
        else:
            mask=msg[2:6]
            content=msg[6:]
        raw_str=''
        for i,d in enumerate(content):
            raw_str += chr(d^mask[i%4])

        print('recv web:',raw_str)
        if is_mask != 1 or opcode == ws_type.WS_CLOSEF_FRAME:
            return raw_str,ws_type.WS_CLOSEF_FRAME
        elif opcode == ws_type.WS_PONG_FRAME:
            return '',ws_type.WS_PONG_FRAME
        elif opcode == ws_type.WS_ERROR_FRAME:
            return '',ws_type.WS_ERROR_FRAME

        return raw_str,0

    def generate_token(self,msg):
        key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key.encode('utf-8')).digest()
        return base64.b64encode(ser_key)

    def socket_close(self):
        global clients,client_lock
        self.__connection.close()
        if client_lock.acquire() == True:
            if self.__userid in clients.keys():
                clients.pop(self.__userid)
            client_lock.release()
        Logger().get_logger().info('WebSocket close the client socket session,the client identify:{0}'.format(self.__userid))

    def run(self):
        Logger().get_logger().info('WebSocket: new WebSocket client joined')
        data=self.__connection.recv(2048)
        if not data:
            Logger().get_logger().warning('WebSocket get null message data,then close the socket')
            self.socket_close()
            return

        headers=self.parse_headers(data)
        token=self.generate_token(headers.get('Sec-WebSocket-Key'))
        response = 'HTTP/1.1 101 WebSocket Protocol Handshake\r\n'\
            'Upgrade:websocket\r\n'\
            'Connection:Upgrade\r\n'\
            'Sec-WebSocket-Accept:{0}\r\n\r\n'.format(str(token)[2:30])

        try:
            if self.__connection._closed == False:
                self.__connection.send(
                    response.encode('utf-8')
                )
            else:
                Logger().get_logger().warning('WebSocket can not send message to client')
                self.socket_close()
                return
        except Exception as e:
            Logger().get_logger().error('WebSocket get error while send websocket connetion protocol websocket:{0}'.format(str(e)))
            self.socket_close()
            return

        global connected_notify_callback
        if connected_notify_callback is not None:
            connected_notify_callback(self.__userid)

        while True:
            try:
                data=self.__connection.recv(2048)
            except socket.error as e:
                Logger().get_logger().error('WebSocket unexcepted error:{0}'.format(str(e)))
                self.socket_close()
                break

            if not data:
                Logger().get_logger().error('WebSocket get null message data,then close the socket')
                self.socket_close()
                break

            v_data,code=self.parse_data(data)

            if code == ws_type.WS_CLOSEF_FRAME:
                global closed_notify_callback
                if closed_notify_callback is not None:
                    closed_notify_callback(self.__userid)
                try:
                    if self.__connection._closed == False:
                        self.__connection.send(encode_webmessage(0x80 | ws_type.WS_CLOSEF_FRAME,v_data))
                    else:
                        Logger().get_logger().warning('WebSocket can not send message to client')
                        self.socket_close()
                        break
                except Exception as e:
                    Logger().get_logger().error('WebSocket get error while send close frame:{0}'.format(str(e)))
                Logger().get_logger().info('WebSocket get close frame the client session code,the username is:{0}'.format(self.__userid))
                self.socket_close()
                break
            elif code == ws_type.WS_PONG_FRAME:
                Logger().get_logger().info('WebSocket get webclient pong message')
                continue
            elif code == ws_type.WS_ERROR_FRAME:
                Logger().get_logger().error('WebSocket get error frame message')
                continue
            if len(v_data) == 0:
                Logger().get_logger().error('WebSocket get null message')
                continue

            global recvdata_notify_callback
            #callback data
            if recvdata_notify_callback is not None:
                recvdata_notify_callback(v_data,self.__userid)

class websocket_server(threading.Thread):
    def __init__(self,host,port):
        super(websocket_server,self).__init__()
        self.__port=port
        self.__host=host

    def run(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind((self.__host,self.__port))
        sock.listen(5)
        Logger().get_logger().info('WebSocket server started')
        global clients,client_lock
        while True:
            connection,address=sock.accept()
            try:
                userid = connection.fileno()
                if client_lock.acquire() == True:
                    clients[userid]=connection
                    Logger().get_logger().info('WebSocket server clients:{0}'.format(clients))
                    client_lock.release()
                thread = websocket_thread(connection, userid)
                thread.setDaemon(True)
                thread.start()
            except socket.timeout:
                Logger().get_logger().error('WebSocket connection timeout')
            except Exception as e:
                Logger().get_logger().error('WebSocket error:{0}'.format(str(e)))


if '__main__' == __name__:
    server = websocket_server('0.0.0.0',5011)
    server.start()
    sleep(10000)