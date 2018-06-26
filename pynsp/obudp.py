from ctypes import *
from pynsp.nisdef import *
import struct
from pynsp import iphelper
from threading import Lock

udp_inited = 0
map_udp_objects=dict()
map_udp_locker = Lock()

def udpio_callback(nise, udpd):
    llink = nise.contents.Link.UdpLink.Link

    map_udp_locker.acquire()
    if llink in map_udp_objects:
        obj = map_udp_objects[llink]
    else:
        map_udp_locker.release()
        return
    map_udp_locker.release()

    try:
        if EVT_RECEIVEDATA == nise.contents.Event:
            length = udpd.contents.e.Packet.Size
            obj.i_recvdata(udpd.contents.e.Packet.Data, length, \
                str(udpd.contents.e.Packet.RemoteAddress, encoding='utf-8'), udpd.contents.e.Packet.RemotePort)

        elif EVT_PRE_CLOSE == nise.contents.Event:
            obj.on_pre_close()

        elif EVT_CLOSED == nise.contents.Event:
            obj.i_closed()

    except KeyError:
        print('dict key error, udp link 0x%08x no found.' % llink)
    except TypeError:
        print(obj)
    # except:
    #     print('dict other error.')


class obudp:
    def __init__(self, myrecv = None):
        global udp_inited
        if 0 == udp_inited:
            solib.udp_init()
            udp_inited += 1

        # initialize self HUDPLINK to 0xFFFFFFFF
        self.link = -1

        # declare io callback function use global method
        self.udpio = udpio_callback_t(udpio_callback)
        self.pkgmaker = None

        # initialize local address info
        self.lhost = '0.0.0.0'
        self.lport = 0

        # direct recv function
        self.myrecv = myrecv

    def __del__(self):
        if self.link > 0:
            self.close()

    def create(self, host = '0.0.0.0', port = 0, flag = UDP_FLAG_NONE)->int:
        self.link = solib.udp_create(self.udpio, host.encode('utf-8'), port, flag)
        if self.link < 0:
            return -1

        map_udp_locker.acquire()
        map_udp_objects[self.link] = self
        map_udp_locker.release()

        # save local address info
        actip = c_uint()
        actport = c_ushort()
        solib.udp_getaddr(self.link, byref(actip), byref(actport))
        self.lhost = iphelper.ip2str(actip.value, iphelper.BE)
        self.lport = actport.value
        return 0

    def send(self, stream, cb, host, port)->int:
        if self.link < 0:
            return -1
        return solib.udp_write(self.link, cb, self.pkgmaker, stream, host.encode('utf-8'), port )

    def close(self):
        if self.link > 0:
            solib.udp_destroy(self.link)

    def i_closed(self):
        link = self.link
        self.link = -1

        map_udp_locker.acquire()
        if link in map_udp_objects:
            map_udp_objects.pop(link) # erase from object set
        map_udp_locker.release()
        
        self.on_closed(link)

    def i_recvdata(self, data, cb, host, port):
        if None != self.myrecv:
            try:
                self.myrecv(data, cb, host ,port)
                return
            except:
                pass
        self.on_recvdata(data, cb, host, port)

    def on_recvdata(self, data, cb, host, port):
        pass

    def on_pre_close(self):
        pass

    def on_closed(self, previous):
        pass