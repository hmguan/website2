from pynsp import singleton as slg
import threading


@slg.singleton
class net_manager():
    def __init__(self):
        self.__pkt_id=0
        # threading.Thread.__init__(self)
        self.__is_exits = False

    def __del__(self):
        self.__is_exits=True

    def allocate_pkt(self):
        self.__pkt_id += 1
        return self.__pkt_id