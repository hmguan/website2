from pynsp.nisdef import *
from pynsp import iphelper
from pynsp import old
from threading import Lock

tcp_inited = int(0)
map_tcp_objects = dict()
map_tcp_locker = Lock()

def tcpio_callback(nise, tcpd):
    llink = nise.contents.Link.TcpLink.Link

    map_tcp_locker.acquire()
    if llink in map_tcp_objects:
        obj = map_tcp_objects[llink]
    else:
        map_tcp_locker.release()
        return
    map_tcp_locker.release()

    try:
        # when parsing c-style pointer, python code need to use 'Structure::contents' object
        if EVT_TCP_ACCEPTED == nise.contents.Event:
            rlink = tcpd.contents.e.Accept.AcceptLink
            obj.on_accepted(rlink)

        elif EVT_RECEIVEDATA == nise.contents.Event:
            length = tcpd.contents.e.Packet.Size
            obj.on_recvdata(tcpd.contents.e.Packet.Data, length)

        elif EVT_PRE_CLOSE == nise.contents.Event:
            obj.on_pre_close()

        elif EVT_CLOSED == nise.contents.Event:
            obj.i_closed()

        elif EVT_TCP_CONNECTED == nise.contents.Event:
            obj.i_connected()

    except KeyError:
        print('dict key error, link 0x%08x no found.' % llink)
    except TypeError:
        print('typeError, obj=', obj)
    # except:
    #     print('dict other error.')

class obtcp(object):
    """
    obtcp class provides an encapsulation of the C-module nshost.so. 
    The object of this class and its derived class can easily use the TCP module function.
    """
    def __init__(self, rlink=-1, tstdef=old.nspdef):
        """
        init library nshost.so for tcp functional
        """

        global tcp_inited
        if 0 == tcp_inited:
            solib.tcp_init()
            tcp_inited += 1

        self.link = rlink
        # self.myclients=dict()

        # declare io callback function use global method
        self.tcpio = tcpio_callback_t(tcpio_callback)

        #declare package maker callback function use global method
        #self.pkgmaker = tcp_packet_maker_t(obtcp.tcp_packet_maker)

        # use nshost built-in package maker to build packet,
        # direct copy memory from input steam to package data
        self.pkgmaker = None

        # initialize self tst struct
        self.tst = tcp_tst_t()
        if tstdef is not None:
            self.tst.parser = tcptst_parse_t(tstdef.tcp_parser)
            self.tst.builder = tcptst_build_t(tstdef.tcp_builder)
        self.tst.cb = 8

        # declare and initialize endpoint info
        self.lhost = '0.0.0.0'
        self.lport = 0
        self.rhost = '0.0.0.0'
        self.rport = 0

        # this object is creat by accept event
        if self.link >= 0:
            solib.tcp_settst(self.link, byref(self.tst))

            map_tcp_locker.acquire()
            map_tcp_objects[self.link] = self
            map_tcp_locker.release()

    def __del__(self):
        print('obtcp __del__')
        self.close()

    def create(self, host='0.0.0.0', port=0)->int:
        """
        create a socket for tcp object, bind on local endpoint host:port
        """
        self.link = solib.tcp_create(self.tcpio, host.encode('utf-8'), port)
        if self.link < 0:
            return -1
        solib.tcp_settst(self.link, byref(self.tst))

        # add object into map
        map_tcp_locker.acquire()
        map_tcp_objects[self.link] = self
        map_tcp_locker.release()
        return 0

    def listen(self, blocklog=5)->int:
        """
        listen for connections on a socket which owned by link of self object

        The backlog argument defines the maximum length to which the queue of pending connections for sockfd may grow.
        If a connection request arrives when the queue is full, the client may receive an error with an indication of ECONNREFUSED or,
        if the underlying protocol supports retransmission, the request may be ignored so that a later reattempt at connection succeeds.
        """
        if self.link < 0:
            return -1
        if solib.tcp_listen(self.link, blocklog) < 0:
            return -1

        # save local address info, pass remote address
        actip = c_uint()
        actport = c_ushort()
        solib.tcp_getaddr(self.link, LINK_ADDR_LOCAL, byref(actip), byref(actport))
        self.lhost = iphelper.ip2str(actip.value, iphelper.BE)
        self.lport = actport.value
        return 0

    def connect(self, host, port)->int:
        """
        connects the socket referred to by link of self object to the address specified by host:port.
        If the connection or binding succeeds, zero is returned.  On error, -1 is returned
        """
        if self.link < 0:
            return -1

        # address info will be filled when callback to i_connected
        # and tst will be set to this link in i_connected procedure
        return solib.tcp_connect(self.link, host.encode('utf-8'), port)

    def connect2(self, host, port)->int:
        """
        connects the socket referred to by link of self object to the address specified by host:port.
        If the connection or binding succeeds, zero is returned.  On error, -1 is returned

        This is an asynchronous method. The correct return value does not mean that the connection is successful.
        The calling thread must determine the final connection state by overwrite the virtual function on_connected.
        """

        if self.link < 0:
            return -1
        return solib.tcp_connect2(self.link, host.encode('utf-8'), port)

    def send(self, stream, cb)->int:
        """
        write package data to the cache of operation system
        parameters:
            stream->bytes   the data pointer of package
            cb->int         size of stream in bytes
        """

        if self.link < 0:
            return -1
        return solib.tcp_write(self.link, cb, self.pkgmaker, stream)

    def close(self):
        """
        destroy current link owned by self object,
        the nshost module will do following:
        1. shutdown the socket of the link object
        2. close the file-descriptor of the socket
        3. release all the memory owned by this link object
        4. always callback and notify by virtual method on_closed
        """

        if self.link > 0:
            solib.tcp_destroy(self.link)

    def i_closed(self):
        link = self.link
        map_tcp_locker.acquire()
        if link in map_tcp_objects:
            map_tcp_objects.pop(link)
        map_tcp_locker.release()
        self.link = -1
        self.on_closed(link)

    def i_connected(self):
        """
        virtual function called by nshost when tcp-synack completed
        """
        actip = c_uint()  # save local/remote address info
        actport = c_ushort()
        solib.tcp_getaddr(self.link, LINK_ADDR_LOCAL, byref(actip), byref(actport))
        self.lhost = iphelper.ip2str(actip.value, iphelper.BE)
        self.lport = actport.value
        solib.tcp_getaddr(self.link, LINK_ADDR_REMOTE, byref(actip), byref(actport))
        self.rhost = iphelper.ip2str(actip.value, iphelper.BE)
        self.rport = actport.value
        # let child class handle the connected event
        self.on_connected()

    def on_accepted(self, rlink):
        """
        virtual function called by nshost when tcp-synack completed
        """
        pass

    def on_recvdata(self, data, cb):
        """
        virtual function called by nshost.
        handle your protocol with overwrite this method.
        """
        pass

    def on_pre_close(self):
        """
        virtual function called by nshost before link closed.
        """
        pass

    def on_closed(self, previous):
        """
        virtual function called by nshost when tcp-fin completed.
        """
        pass


    def on_connected(self):
        """
        virtual function called by nshost when tcp-syn completed.
        """
        pass
