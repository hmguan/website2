from pynsp import obtcp as tcp
from .mtproto import mthead,cread,login,cwrite,error_status
import random
from pynsp.encrypt import *
import hashlib
import threading
import copy
import time
from .mtproto import view_data
from pynsp.waite_handler import *
from .mtproto.viewtype import *
from agvmt import mt_var_info


class mt_session(tcp.obtcp):
    def __init__(self,rlink = -1,notify_closed=None):
        super(mt_session, self).__init__(rlink)
        self.__publickey=bytes()
        self.__robot_id=-1
        self.__target_host=""
        self.__connect=-1
        self.__error=-1#车的实时状态
        self.__mutex = threading.RLock()
        self.__data_mutex=threading.RLock()
        self.__timestamp = int(round(time.time() * 1000))
        self.__notify_closed = notify_closed
        self.__navigation_cache=view_data.navigation_t()
        self.__vehicle_cache=view_data.vehicle_t()
        self.__operation_cache=view_data.operation_t()
        self.__optpar_cache=view_data.optpar_t()
        self.__var_list=list()
        self.__var_data=b''
        self.__is_appoint=True
        return

    def __del__(self):
        print("mt_session del, robot_id:%d" % self.__robot_id)
        return

    def on_accepted(self, rlink):
        client_link = mt_session(rlink)

    def on_recvdata(self, data, cb):
        phead = mthead.proto_head()
        phead.build(data, 0)
        # print('mt---recv packet,type=', hex(phead.type),phead.size,phead.err)

        self.__mutex.acquire()
        self.__timestamp = int(round(time.time() * 1000))
        self.__mutex.release()

        pkt_id = phead.id
        if phead.err.value < 0:
            wait_handler().wait_singal(pkt_id.value)
            return


        if login.PKTTYPE_PRE_LOGIN == phead.type:
            self.__connect = 0
            pre_login = login.proto_pre_login()
            pre_login.build(data, 0)
            self.try_login(pre_login.key.value)

        elif login.PKTTYPE_LOGIN_ROBOT_ACK == phead.type:
            login_ack = login.proto_login_ack()
            login_ack.build(data, 0)
            if login_ack.err == 0:
                self.__connect = 1
                print('mt---login mt successful.')
            else:
                print('mt---login failed.')

        elif mthead.PKTTYPE_KEEPALIVE_TCP_ACK==phead.type:
            pass

        elif cread.PKTTYPE_COMMON_READ_BYID_ACK == phead.type:
            common_ack=cread.proto_common_vct()
            common_ack.build(data,0)
            # print('data---',common_ack.items[0].var_data.value)
            if not self.__is_appoint:
                self.recv_var_data(pkt_id,common_ack.items[0].var_data.value)
                return
            # print('mt---on common read ack,type:', common_ack.items[0].var_id)
            if common_ack.items[0].var_id == kVarFixedObject_Vehide:
                if common_ack.length()== 48:
                    pkterror=error_status.proto_error()
                    pkterror.build(common_ack.items[0].var_data.value,0)
                    self.__error = pkterror.error
                else:
                    self.recv_vehicle_data(pkt_id,common_ack.items[0].var_data.value)

            elif common_ack.items[0].var_id == kVarFixedObject_Navigation:
                self.recv_navigation_data(pkt_id,common_ack.items[0].var_data.value)
            elif common_ack.items[0].var_id ==kVarFixedObject_Operation:
                self.recv_operation_data(pkt_id,common_ack.items[0].var_data.value)
            elif common_ack.items[0].var_id ==kVarFixedObject_OptPar:
                self.recv_optpar_data(pkt_id,common_ack.items[0].var_data.value)


        elif mthead.PKTTYPE_DBG_CLEAR_FAULT_ACK==phead.type:
            print('mt--clear ack')

        elif cwrite.PKTTYPE_COMMON_WRITE_BYID_ACK==phead.type:
            print('mt--stop_ack')

        elif mthead.PKTTYPE_DBG_VARLS_ACK==phead.type:
            var_list=mthead.proto_var_report_items()
            var_list.build(data,0)
            self.recv_var_list_data(pkt_id,var_list.items)

        else:print('mt---not type')


    def on_connected(self):
        print('mt---connect to mt %s:%d' % (self.rhost, self.rport))

    def on_closed(self, previous):
        self.__connect = -1
        print('mt---mtlink closed%s:%d' % (self.rhost, self.rport))
        if self.__notify_closed is not None:
            self.__notify_closed(self.__robot_id)


    def try_connect(self,ipv4,port,robot_id):
        if self.create() < 0:
            return -1

        self.__target_host = ipv4
        self.__robot_id=robot_id

        if self.connect(ipv4,port) < 0:
            self.close()
            print("failed to connect to mt endpoint:",ipv4)
            return -1



        #if self.__connect==0:
        return 0
        #else:return -1

    def try_login(self,key):
        login_ack = login.proto_login()

        req = bytearray(32)
        for i in range(32):
            req[i] = random.randint(0, 254) & 0xFF
        login_ack.ori(req)

        out, outcb = encrypt(req, key)
        enc = bytearray(outcb)
        for i in range(outcb):
            enc[i] = out[i]
        al = hashlib.md5()
        al.update(enc)
        login_ack.enc(al.digest())

        login_ack.phead.size(login_ack.length())
        stream = login_ack.serialize()
        return self.send(stream, login_ack.length())

    def disconnect_net(self):
        self.close()

    def get_network_status(self):
        return self.__connect

    def get_status(self):
        self.__is_appoint=True
        cread_item = cread.proto_common_read_item()
        cread_item.var_id(kVarFixedObject_Vehide)
        cread_item.var_type(0)
        cread_item.var_offset(177)
        cread_item.var_length(4)

        pkt_cread = cread.proto_common_read()
        pkt_cread.items.append(cread_item)

        pkt_cread.phead.size(pkt_cread.length())
        stream = pkt_cread.serialize()
        self.send(stream, pkt_cread.length())

    def agv_status(self):
        return int(self.__error)

    def get_timestamp(self):
        self.__mutex.acquire()
        timestamp=copy.deepcopy(self.__timestamp)
        self.__mutex.release()
        return timestamp

    def get_target_host(self):
        return self.__target_host

    def post_alive_pkt(self):
        pkt = mthead.proto_keepalive()
        stream = pkt.serialize()
        self.send(stream, pkt.length())

    def robot_error_status(self,state):
        print('mt---error:',state)

    def clear_error(self):
        pkt_clear = mthead.proto_clearfault()
        stream=pkt_clear.serialize()
        self.send(stream,pkt_clear.length())

    def set_stop_emergency(self):
        cwrite_stop=cwrite.proto_common_write_item()
        cwrite_stop.var_id(kVarFixedObject_Vehide)
        cwrite_stop.var_type(1)
        cwrite_stop.var_offset(169)
        cwrite_stop.var_data(b'1')

        pkt_cwrite=cwrite.proto_common_write()
        pkt_cwrite.items.append(cwrite_stop)
        pkt_cwrite.phead.size(pkt_cwrite.length())
        stream = pkt_cwrite.serialize()

        stream = pkt_cwrite.serialize()
        self.send(stream,pkt_cwrite.length())

    def get_nav_data(self):
        self.__is_appoint=True
        pkt_nav = view_data.navigation_t()
        cread_item = cread.proto_common_read_item()
        cread_item.var_id(kVarFixedObject_Navigation)
        cread_item.var_type(1)
        cread_item.var_offset(0)
        cread_item.var_length(pkt_nav.length())

        pkt_cread = cread.proto_common_read()
        pkt_cread.items.append(cread_item)
        pkt_id = wait_handler().allocat_pkt_id()
        pkt_cread.phead.id(pkt_id)
        pkt_cread.phead.size(pkt_cread.length())
        stream = pkt_cread.serialize()
        self.send(stream, pkt_cread.length())
        return pkt_id

    def get_veh_data(self):
        self.__is_appoint = True
        pkt_veh = view_data.vehicle_t()
        cread_item = cread.proto_common_read_item()
        cread_item.var_id(kVarFixedObject_Vehide)
        cread_item.var_type(1)
        cread_item.var_offset(0)
        cread_item.var_length(pkt_veh.length())#349

        pkt_cread = cread.proto_common_read()
        pkt_cread.items.append(cread_item)
        pkt_id = wait_handler().allocat_pkt_id()
        pkt_cread.phead.id(pkt_id)
        pkt_cread.phead.size(pkt_cread.length())
        stream = pkt_cread.serialize()
        self.send(stream, pkt_cread.length())
        return pkt_id

    def get_ope_data(self):
        self.__is_appoint = True
        pkt_ope=view_data.operation_t()
        cread_item = cread.proto_common_read_item()
        cread_item.var_id(kVarFixedObject_Operation)
        cread_item.var_type(0)
        cread_item.var_offset(0)
        cread_item.var_length(pkt_ope.length())

        pkt_cread = cread.proto_common_read()
        pkt_cread.items.append(cread_item)
        pkt_id = wait_handler().allocat_pkt_id()
        pkt_cread.phead.id(pkt_id)
        pkt_cread.phead.size(pkt_cread.length())
        stream = pkt_cread.serialize()
        self.send(stream, pkt_cread.length())
        return pkt_id

    def get_opt_data(self):
        self.__is_appoint = True
        pkt_opt = view_data.optpar_t()
        cread_item = cread.proto_common_read_item()
        cread_item.var_id(kVarFixedObject_OptPar)#kVarFixedObject_OptPar
        cread_item.var_type(1)
        cread_item.var_offset(0)
        cread_item.var_length(pkt_opt.length())

        pkt_cread = cread.proto_common_read()
        pkt_cread.items.append(cread_item)
        pkt_id = wait_handler().allocat_pkt_id()
        pkt_cread.phead.id(pkt_id)
        pkt_cread.phead.size(pkt_cread.length())
        stream = pkt_cread.serialize()
        self.send(stream, pkt_cread.length())
        return pkt_id

    def get_var_list(self):
        var_pkt=mthead.proto_dug_varls()
        pkt_id = wait_handler().allocat_pkt_id()
        var_pkt.id(pkt_id)
        stream=var_pkt.serialize()
        self.send(stream,var_pkt.length())
        return pkt_id

    def get_var_data(self,var_id):
        type_id=-1
        for item in self.__var_list:
            if item.var_id==var_id:
                type_id=item.var_type
                break
        if type_id==-1:
            return -1,-1
        self.__is_appoint = False
        pkt_opt = view_data.optpar_t()
        cread_item = cread.proto_common_read_item()
        cread_item.var_id(var_id)
        cread_item.var_offset(0)
        length=mt_var_info.get_var_read_length(type_id)
        if length is None:
            return -1,-1
        cread_item.var_length(length)

        pkt_cread = cread.proto_common_read()
        pkt_cread.items.append(cread_item)
        pkt_id = wait_handler().allocat_pkt_id()
        pkt_cread.phead.id(pkt_id)
        pkt_cread.phead.size(pkt_cread.length())
        stream = pkt_cread.serialize()
        self.send(stream, pkt_cread.length())
        return pkt_id,type_id

    def recv_navigation_data(self, pkt_id ,data):
        self.__navigation_cache.build(data,0)
        wait_handler().wait_singal(pkt_id.value)

    def recv_vehicle_data(self,pkt_id,data):
        self.__vehicle_cache.build(data,0)
        wait_handler().wait_singal(pkt_id.value)

    def recv_operation_data(self,pkt_id,data):
        self.__operation_cache.build(data,0)
        wait_handler().wait_singal(pkt_id.value)

    def recv_optpar_data(self,pkt_id,data):
        self.__optpar_cache.build(data,0)
        wait_handler().wait_singal(pkt_id.value)

    def recv_var_list_data(self,pkt_id,data):
        self.__var_list=data
        wait_handler().wait_singal(pkt_id.value)

    def recv_var_data(self,pkt_id,data):
        self.__data_mutex.acquire()
        self.__var_data=data
        self.__data_mutex.release()
        wait_handler().wait_singal(pkt_id.value)

    def get_local_navigation_data(self):
        return self.__navigation_cache

    def get_local_vehicle_data(self):
        return self.__vehicle_cache

    def get_local_operation_data(self):
        return self.__operation_cache

    def get_local_optpar_data(self):
        return self.__optpar_cache

    def get_local_var_list(self):
        return self.__var_list

    def get_local_var_data(self):
        return self.__var_data




