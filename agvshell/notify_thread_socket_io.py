from pynsp.wait import *
import threading
from copy import deepcopy

class notify_thread(object):
    """docstring for notify_thread"""
    def __init__(self):
        super(notify_thread, self).__init__()
        #{msg_type:[],}
        self.__notify_queue = dict()
        self.__thread_exit = False
        self.__mutex_queue = threading.RLock()
        self.__wait_handle = waitable_handle(False)
        self.__notify_cb = None
        self.__check_notify = None
        self.__init_thread()

    def __del__(self):
        self.__thread_exit = True
        self.__wait_handle.sig()
        if self.__check_notify:
            self.__check_notify.join()
            del self.__check_notify
        pass

    def __init_thread(self):
        if not(self.__check_notify):
            self.__check_notify=threading.Thread(target=notify_thread.socket_io_notify_thread,args=(self,))
            self.__check_notify.setDaemon(True)
            self.__check_notify.start()
        pass

    def socket_io_notify_thread(self):
        check_time = 1000
        while(self.__thread_exit is not True):
            if 0 == len(self.__notify_queue):
                self.__wait_handle.wait(check_time)
            else:
                notify_dict = dict()
                self.__mutex_queue.acquire()
                notify_dict = self.__notify_queue
                self.__notify_queue.clear()
                self.__mutex_queue.release()

                if self.__notify_cb:
                    for (msg_type,data) in notify_dict.items():
                        self.__notify_cb(msg_type,data)
                self.__wait_handle.wait(check_time)

    def add_notify(msg_type,data):
        self.__mutex_queue.acquire()
        if msg_type not in self.__notify_queue:
            self.__notify_queue[msg_type] = list()
        self.__notify_queue[msg_type].append(data)
        self.__mutex_queue.release()

    def register_socketio_notify(self,socketio_notify):
        self.__notify_cb = socketio_notify