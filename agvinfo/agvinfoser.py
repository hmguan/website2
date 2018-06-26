from pynsp import obtcp
from pynsp import obudp
from agvshell.shproto import report as agvshreport
from agvshell.shproto.proto_head import *
import threading
from time import sleep
from agvmt.mtproto import discover
from agvinfo import agvinfodata
from copy import deepcopy

class agvinfo_runtime:
    aid = 0
    def __init__(self, _id, _host, _port, _mac, _shport):
        self.id = _id
        self.host = _host
        self.port = _port
        self.mac = _mac
        self.shport = _shport
        self.alive = 3
        self.mtready = False

agv_online = dict() # map<mac, agvinfo_runtime>
mutex_agvonline = threading.RLock()
mutex_agvcfg = threading.RLock() # protected theR agvinfodata.dict_xml_agvinfo
current_max_agvid_config = 0

def agvinfo_search_bymac(mac):
    agvbase = None
    mutex_agvcfg.acquire()
    for n in agvinfodata.dict_xml_agvinfo:
        if mac == n.hwaddr:
            agvbase = deepcopy(n)
            break
    mutex_agvcfg.release()
    return agvbase

def agvinfo_search_unused():
    agvbase = None
    mutex_agvcfg.acquire()
    for n in agvinfodata.dict_xml_agvinfo:
        if 0 == len(n.hwaddr):
            agvbase = deepcopy(n)
            break
    mutex_agvcfg.release()
    return agvbase

# mutil-inherit will call __init__ method from left to right
# overwritten method of parent class, by the same order
class agvinfo_shellser(obudp.obudp, threading.Thread):
    def __init__(self, _notify_changed = None):
        super(agvinfo_shellser, self).__init__()
        threading.Thread.__init__(self)
        self.notify_changed = _notify_changed
        self.__terminate = False

    def __del__(self):
        print('agvinfo_shellser __del__')

    def __select_agv_bymac(self, _rep, _from, _port):
        global current_max_agvid_config
        mutex_agvonline.acquire()
        if _rep.mac.value not in agv_online:
            mutex_agvonline.release()

            # select agv from total table, not need locked by mutex_agvonline
            agv_exist = agvinfo_search_bymac(_rep.mac.value)
            if None != agv_exist:
                # use existing agv item
                agv = agvinfo_runtime(agv_exist.vhid, _from, _port, _rep.mac.value, _rep.sh_port)
            else:
                agv_unsed = agvinfo_search_unused()
                if None != agv_unsed:
                    agv = agvinfo_runtime(agv_unsed.vhid, _from, _port, _rep.mac.value, _rep.sh_port)
                else:
                    # increase current max agvid, and then, push it into runtime queue
                    current_max_agvid_config += 1
                    agv = agvinfo_runtime(current_max_agvid_config, _from, _port, _rep.mac.value, _rep.sh_port)
            return agv, True

        else:
            agv = agv_online[_rep.mac.value]
            mutex_agvonline.release()
            return agv, False

    def on_shell_report(self, _data, _cb, _from, _port):
        rep = agvshreport.agvsh_local_report()
        rep.build(_data, 0)

        if len(req.mac.value) < 4:
            return
        #print('online:{0},{1},{2}'.format(_from,_port,rep.sh_port))
        need_notify = False

        # choose agv itme to save online information
        agv, new = self.__select_agv_bymac(rep, _from, _port)
        if not new:
            mutex_agvonline.acquire()
            agv.host = _from
            agv.port = _port
            agv.shport = rep.sh_port
            # reset keepalive counter
            agv.alive = 3
            mutex_agvonline.release()
        else:
            mutex_agvonline.acquire()
            agv_online[agv.mac] = agv
            mutex_agvonline.release()
            print('aginfoser agv [%d]%s online.' % (agv.id, agv.mac))

            # update config file any way
            cfgagv = agvinfodata.agvinfo_t()
            cfgagv.vhid = agv.id
            cfgagv.inet = agv.host
            cfgagv.shport = agv.shport
            cfgagv.hwaddr = agv.mac
            mutex_agvcfg.acquire()
            agvinfodata.update_agvinfo(cfgagv)
            mutex_agvcfg.release()

            # need to call callback method if existed
            need_notify = True

        # notify calling thread, agv info changed
        if None != self.notify_changed and need_notify:
            self.notify_changed()

    def on_mt_discover_ack(self, _from):
        print('on_mt_discover_ack')
        mutex_agvonline.acquire()
        ls_keys = list(agv_online.keys())
        for i in ls_keys:
            agv = agv_online[i]
            if agv.host == _from:
                agv.mtready = True
                print('[', agv.id, ']', agv.host,'mt ready')
                need_notify = True
                break
        mutex_agvonline.release()

        print('notify:{0},need_notify:{1}'.format(self.notify_changed,need_notify))
        if None != self.notify_changed and need_notify:
            self.notify_changed()

    def on_recvdata(self, _data, _cb, _from, _port):
        # parse report package
        phead = proto_head()
        phead.build(_data, 0)
        if phead.type == agvshreport.kAgvShellProto_LocalInfo:
            self.on_shell_report(_data, _cb, _from, _port)
        elif phead.type == discover.PKTTYPE_KEEPALIVE_UDP_ACK:
            self.on_mt_discover_ack(_from)

    def on_closed(self, _previous):
        self.__terminate = True
        self.join()

    def run(self):
        while not self.__terminate:
            need_notify = False
            mutex_agvonline.acquire()

            # if not convert to list type,code in 'for' block will get following error:
            # RuntingError'dictionary changed size during iteration'
            ls_keys = list(agv_online.keys())
            for i in ls_keys:
                agv = agv_online[i]
                agv.alive -= 1
                if agv.alive == 0:
                    print('aginfoser agv [%d]%s has been removed.' % (agv.id, agv.mac))
                    need_notify = True
                    del(agv_online[i])

                # condition for test motion_template is existed.
                elif agv.mtready == False:
                    self.__test_mtready(agv.host)
            mutex_agvonline.release()

            # notify calling thread, agv info changed
            if None != self.notify_changed and need_notify:
                self.notify_changed()

            # 3 times * 2 seconds, keepalive failed.
            sleep(2)

    def create(self, _host = '0.0.0.0', _port = 9022)->int:
        self.start()
        return super(agvinfo_shellser, self).create(host = _host, port = _port)

    def __test_mtready(self, _host, _port = 4409):
        pkt_discover_mt = discover.proto_discover_mt()
        pkt_discover_mt.phead.size(pkt_discover_mt.length())
        stream = pkt_discover_mt.serialize()
        self.send(stream, pkt_discover_mt.length(), _host, _port)

    def shclosed(self, _mac):
        need_notify = False
        mutex_agvonline.acquire()
        if _mac not in agv_online:
            pass
        else:
            agv = agv_online[_mac]
            print('aginfoser agv [%d]%s has been force removed.' % (agv.id, agv.mac))
            del(agv_online[_mac])
            need_notify = True
        mutex_agvonline.release()

        if need_notify:
            self.notify_changed()

    def mtclosed(self, _mac):
        need_notify = False
        mutex_agvonline.acquire()
        if _mac not in agv_online:
            pass
        else:
            agv = agv_online[_mac]
            print('aginfoser agv [%d]%s mt closed.' % (agv.vhid, agv.mac))
            agv.mtready = False
            need_notify = True
        mutex_agvonline.release()

        if need_notify:
            self.notify_changed()

ser = None

def agvinfoser_startup(_host = '0.0.0.0', _port = 9022, _notify_changed = None)->int:
    global ser
    global current_max_agvid_config

    # load agvinfo from config file agv_info.xml
    agvinfodata.load_agvinfo_xml()

    # calc maximum vehicle id of current agv list
    for n in agvinfodata.dict_xml_agvinfo:
        if (type(n.vhid) == int) and (n.vhid > current_max_agvid_config):
            current_max_agvid_config = n.vhid
    print('current maximum agvid=', current_max_agvid_config)

    # create udp service
    if ser == None:
        ser = agvinfo_shellser(_notify_changed)
    if ser.create(_host, _port) < 0:
        print('failed create udp server for agvinfo.')
        del(ser)
        ser = None
        return -1

    print('agvinfo server startup successful.')
    return 0

def agvinfoser_shclosed(_mac):
    ser.shclosed(_mac)

def agvinfoser_mtclosed(_mac):
    ser.mtclosed(_mac)

def agvinfoser_stop():
    global ser
    ser.close()

    # threading.Thread can only start once
    # is necessary to delete @ser object when stop method called 
    del(ser)
    ser = None

def agvinfoser_getagvs()->dict:
    mutex_agvonline.acquire()
    d = agv_online.copy()
    mutex_agvonline.release()
    return d

def agvinfoser_getoffline()->list:
    mutex_agvonline.acquire()
    online = agv_online.copy()
    mutex_agvonline.release()

    mutex_agvcfg.acquire()
    config = deepcopy(agvinfodata.dict_xml_agvinfo)
    mutex_agvcfg.release()

    offline = list()
    for c in config:
        if (len(c.hwaddr) == 0) or (c.hwaddr not in online):
            offline.append(c)
    return offline