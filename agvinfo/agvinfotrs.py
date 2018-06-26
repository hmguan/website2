from pynsp import obtcp
import threading
from time import sleep
from agvinfo import agvinfodata
from copy import deepcopy
from agvmt.mtproto import mthead
from agvinfo import agvinfoproto
from agvinfo.agvinfoser import mutex_agvcfg
import pdb
import time

dhcp_data_change = False
SESSION_TIMEOUT_TIMESTAMP=30000
PktId = 0

def dhcp_online_change():
    update_status(True)

def is_need_update():
    global dhcp_data_change
    return dhcp_data_change

def update_status(status):
    global dhcp_data_change
    dhcp_data_change = status

def getPktId():
    global PktId
    PktId = PktId +1
    return PktId

class agvinfo_tcptrs(obtcp.obtcp):
    def __init__(self, _rlink=-1,disconncet_callback = None):
        super(agvinfo_tcptrs, self).__init__(rlink = _rlink)
        self.__thread_exit = False
        self.__map_tcp_session = {}
        self.__dis_con_callback =disconncet_callback
        self.__map_mutex = threading.RLock()
        self.__thread_check_state = None
        self.__timestamp=int(round(time.time() * 1000))

    def __del__(self):
        pass

    def __on_getagvinfo(self, _head):
        ack = agvinfoproto.proto_req_agvinfo()
        from agvinfo.agvinfoser import agvinfoser_getagvs

        # method for load
        ack.method(1)
        # info source
        agvbase = agvinfodata.get_agvinfo()
        agv_online = agvinfoser_getagvs()
        for c in agvbase:
            item = agvinfoproto.proto_agvinfo()
            item.vhid(c.vhid)
            item.vhtype(c.vhtype)
            item.inet(c.inet)
            item.mtport(c.mtport)
            item.shport(c.shport)
            item.ftsport(c.ftsport)
            item.hwaddr(c.hwaddr)
            if (0 == len(c.hwaddr)) or (c.hwaddr not in agv_online):
                item.status(agvinfoproto.AS_OFFLINE)
            else:
                item.status(agvinfoproto.AS_ONLINE)

            # append attribute
            for attr in c.attrs:
                attribute = agvinfoproto.proto_agvattribute()
                attribute.name(attr.name)
                attribute.describe(attr.describe)
                item.attrs.append(attribute)
            ack.info.append(item)

        # build head of package
        ack.head.id(_head.id)
        ack.head.type(_head.type)
        ack.head.size(ack.length())
        # make packet stream
        # pdb.set_trace()
        stream = ack.serialize()
        self.send(stream, ack.length())

    def __on_setagvinfo(self, _data):
        req = agvinfoproto.proto_req_agvinfo()
        # pdb.set_trace()
        if 0 >= req.build(_data, 0):
            self.__ack_agvinfo_packet(req.head.id,agvinfoproto.kAgvInfoProto_set_agvinfo,agvinfoproto.KAgvInfo_Errno_Failed)
            return 

        list_agvinfo=[]
        for item in req.info :
            agvinfos = agvinfodata.agvinfo_t()
            agvinfos.vhid = item.vhid
            agvinfos.vhtype = item.vhtype
            agvinfos.inet = item.inet.value
            agvinfos.mtport = item.mtport
            agvinfos.shport = item.shport
            agvinfos.ftsport = item.ftsport
            agvinfos.hwaddr = item.hwaddr.value

            # append attribute
            for a in item.attrs :
                attr = agvinfodata.proto_agvattribute_t()
                attr.describe = a.describe.value
                attr.name = a.name.value
                agvinfos.attrs.append(attr)

            list_agvinfo.append(agvinfos)

        # pdb.set_trace()
        # agvinfodata.set_agvinfo(list_agvinfo)

        self.__ack_agvinfo_packet(req.head.id,agvinfoproto.kAgvInfoProto_set_agvinfo,agvinfoproto.KAgvInfo_Errno_Ok)
        update_status(True)
        return

    def __on_keepalive(self, _head):
        ack = mthead.proto_head(_id=_head.id, _type=agvinfoproto.kAgvInfoProto_heart_beat_ack, _size=24)
        self.send(ack.serialize(), ack.length())

    def get_timestamp(self):
        return self.__timestamp

    def __ack_agvinfo_packet(self, pktId ,acktype, err):
        ack = agvinfoproto.proto_req_agvinfo()
        ack.method(1)
        ack.head.id(pktId)
        ack.head.type(acktype)
        ack.head.err(err)
        ack.head.size(ack.length())
        stream = ack.serialize()
        self.send(stream, ack.length())

    def __keepalive(self) ->int:
        heartbeat = mthead.proto_head(_id=getPktId(),_type=agvinfoproto.kAgvInfoProto_heart_beat, _size=24)
        return self.send(heartbeat.serialize(),heartbeat.length())

    def start(self, _host = '0.0.0.0', _port = 9022)->int:
        if super(agvinfo_tcptrs, self).create(_host, _port) < 0:
            return -1
        if None == self.__thread_check_state:
            # pdb.set_trace()
            self.__thread_check_state = threading.Thread(target=self.thread_check_notify)
            self.__thread_check_state.setDaemon(True)
            self.__thread_check_state.start()

        return super(agvinfo_tcptrs,self).listen()

    def on_recvdata(self, data, cb):
        head = mthead.proto_head()
        head.build(data, 0)
        self.__timestamp = int(round(time.time() * 1000))
        if head.type.value is agvinfoproto.kAgvInfoProto_heart_beat:
            self.__on_keepalive(head)
        if head.type.value is agvinfoproto.kAgvInfoProto_get_agvinfo:
            self.__on_getagvinfo(head)
        if head.type.value is agvinfoproto.kAgvInfoProto_set_agvinfo:
            self.__on_setagvinfo(data)

    def on_accepted(self,_rlink):
        session = agvinfo_tcptrs(_rlink=_rlink, disconncet_callback = self.remove_link)
        self.__map_mutex.acquire()
        self.__map_tcp_session[_rlink] = session
        self.__map_mutex.release()

    def on_closed(self,previous):
        if None != self.__dis_con_callback:
            self.__dis_con_callback(previous)

    def remove_link(self,_rlink):
        self.__map_mutex.acquire()
        if _rlink in self.__map_tcp_session:
            del(self.__map_tcp_session[_rlink])
        self.__map_mutex.release()

    def thread_check_notify(self):
        global SESSION_TIMEOUT_TIMESTAMP
        while self.__thread_exit is False:
            if is_need_update() is True:
                # pdb.set_trace()
                self.notify_all()
                update_status(False)

            current_timestamp = int(round(time.time() * 1000))
            close_list = []
            self.__map_mutex.acquire()
            for link in self.__map_tcp_session:
                if None != self.__map_tcp_session[link]:
                    dec_timestamp = current_timestamp - self.__map_tcp_session[link].get_timestamp()
                    # print('thread_check_notify',dec_timestamp,current_timestamp,self.__map_tcp_session[link].get_timestamp())
                    if dec_timestamp > SESSION_TIMEOUT_TIMESTAMP:
                        close_list.append(self.__map_tcp_session[link])
                    elif dec_timestamp > 4000:
                        if self.__map_tcp_session[link].__keepalive() < 0:
                            close_list.append(self.__map_tcp_session[link])
            self.__map_mutex.release()

            for session in close_list:
                session.close()

            sleep(2)

    def notify_all(self):
        tcp_list = []
        # Reduce lock occupancy time
        self.__map_mutex.acquire()
        for link in self.__map_tcp_session:
            if None != self.__map_tcp_session[link]:
                tcp_list.append(self.__map_tcp_session[link])
        self.__map_mutex.release()
        
        ack = mthead.proto_head(_id = 0, _type=agvinfoproto.kAgvInfoProto_update_notify, _size=24)
        for tcp_object in tcp_list:
            ack.head.id(getPktId())
            tcp_object.send(ack.serialize(),ack.length())

trs = None

def agvinfotrs_startup(_host = '0.0.0.0', _port = 9022)->int:
    global trs
    if trs == None:
        trs = agvinfo_tcptrs()
    return trs.start(_host, _port)
