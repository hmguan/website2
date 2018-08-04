from pynsp import singleton
from pynsp import wait

@singleton.singleton
class wait_handler():
    def __init__(self):
        self.__wait_object = dict()
        self.__pkt_id= 0
        pass

    def wait_simulate(self,sid,timeout_time):
        if self.__wait_object.__contains__(sid) == False:
            return -1
        if self.__wait_object[sid].wait(timeout_time) == False:
            return -1
        return 0

    def wait_singal(self,sid):
        if self.__wait_object.__contains__(sid) == True:
            self.__wait_object[sid].sig()
            # self.__wait_object[sid].reset()

    def wait_destory(self,sid):
        if self.__wait_object.__contains__(sid) == False:
            return -1
        del self.__wait_object[sid]

    def allocat_pkt_id(self):
        self.__pkt_id += 1
        if self.__wait_object.__contains__(self.__pkt_id) == True:
            return -1
        w_obj = wait.waitable_handle(False)
        self.__wait_object[self.__pkt_id] = w_obj
        return self.__pkt_id