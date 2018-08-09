# -*- coding: utf-8 -*-

from pynsp import singleton as slt
from agvmt import mt_session
from agvmt.mtproto import view_data,viewtype,mthead
import threading
from time import sleep
import time
from pynsp.waite_handler import *
from agvinfo import agvinfoser
from pynsp.wait import *
import copy
from agvmt import mt_var_info
import errtypes
from pynsp.logger import *

#监测心跳超时时间戳差
CHECK_ALIVE_TIMESTAMP_OUT=6000
#
mt_status_notify=None
@slt.singleton
class mt_manage():
    def __init__(self):
        self.__robot_lnk = {}
        self.__agv_status = {}
        self.__is_exist_th = False
        self.__mutex = threading.RLock()
        self.__check_timeout = threading.Thread(target=mt_manage.check_session_timeout, args=(self,))
        self.__check_timeout.setDaemon(True)
        self.__check_timeout.start()
        pass

    def __del__(self):
        self.__is_exist_th = True
        self.__check_timeout.join()
        print('mt_manage __del__')


    def login_to_mt(self,robot_id,ipv4,port,notify_callback = None):
        if robot_id in self.__robot_lnk.keys():
            print('the mt target:',ipv4,' is already exits.')
            return

        session_link=mt_session.mt_session(notify_closed = notify_callback)
        print('mt try to connect to ipv4:',ipv4)
        if session_link.try_connect(ipv4, 4409, robot_id) < 0:
            print('mt_connect',ipv4,'failed')
            return

        for index in range(0,50):
            if session_link.get_network_status()==1:
                self.__mutex.acquire()
                self.__robot_lnk[robot_id] = session_link
                self.__mutex.release()
                print('__robot_lnk', robot_id, '=', session_link)
                self.__agv_status[robot_id] = 0
                break
            else:
                sleep(0.1)

    def dis_connect(self,id):
        if self.__robot_lnk.__contains__(id) == False:
            return

        self.__mutex.acquire()
        session_link=self.__robot_lnk[id]
        self.__mutex.release()
        session_link.disconnect_net()

    def clear_agv_error(self,robot_list):
        self.__mutex.acquire()
        for robot_id in robot_list:
            if int(robot_id) in self.__robot_lnk.keys():
                self.__robot_lnk[int(robot_id)].clear_error()
        self.__mutex.release()

    def get_navigation_data(self,id):
        if self.__robot_lnk.__contains__(id) == False:
            return view_data.navigation_t()#返回空结构体给页面

        self.__mutex.acquire()
        session_link=self.__robot_lnk[id]
        self.__mutex.release()

        pkt_id = session_link.get_nav_data()
        nav_data=view_data.navigation_t()
        if wait_handler().wait_simulate(pkt_id,5000) >= 0:
            nav_data = session_link.get_local_navigation_data()
            wait_handler().wait_destory(pkt_id)
        return nav_data

    def get_vehicle_data(self,id):
        if self.__robot_lnk.__contains__(id) == False:
            return view_data.vehicle_t()
        self.__mutex.acquire()
        session_link=self.__robot_lnk[id]
        self.__mutex.release()

        pkt_id = session_link.get_veh_data()
        veh_data=view_data.vehicle_t()
        if wait_handler().wait_simulate(pkt_id,5000) >=0:
            veh_data = session_link.get_local_vehicle_data()
            wait_handler().wait_destory(pkt_id)
        return veh_data

    def get_operation_data(self,id):

        if self.__robot_lnk.__contains__(id) == False:
            return {}
        self.__mutex.acquire()
        session_link = self.__robot_lnk[id]
        self.__mutex.release()

        pkt_id=session_link.get_ope_data()
        oper_data=view_data.operation_t()
        if wait_handler().wait_simulate(pkt_id,5000) >=0:
            oper_data = session_link.get_local_operation_data()
            wait_handler().wait_destory(pkt_id)
        return oper_data

    def get_optpar_data(self,id):
        if self.__robot_lnk.__contains__(id) == False:
            return {}
        self.__mutex.acquire()
        session_link=self.__robot_lnk[id]
        self.__mutex.release()

        pkt_id=session_link.get_opt_data()
        opt_data=view_data.optpar_t()
        if wait_handler().wait_simulate(pkt_id,5000)>=0:
            opt_data=session_link.get_local_optpar_data()
            wait_handler().wait_destory(pkt_id)
        return opt_data

    def set_stop(self,robot_list):
        self.__mutex.acquire()
        for robot_id in robot_list:
            if int(robot_id) in self.__robot_lnk.keys():
                self.__robot_lnk[int(robot_id)].set_stop_emergency()
        self.__mutex.release()

    def check_session_timeout(self):
        while self.__is_exist_th == False:
            self.__mutex.acquire()
            keys = list(self.__robot_lnk.keys())
            self.__mutex.release()
            for key_item in keys:
                self.__mutex.acquire()
                session_link = self.__robot_lnk.get(key_item)
                self.__mutex.release()
                if session_link is None:
                    continue

                host = session_link.get_target_host()
                current_timestamp = int(round(time.time()*1000))
                session_time = session_link.get_timestamp()
                if (current_timestamp - session_time) > CHECK_ALIVE_TIMESTAMP_OUT:
                    #超时，则直接关闭连接
                    Logger().get_logger().error('the target endpoint {0} check timeout,current timestamp:{1}'.format(host,current_timestamp))
                    print('the target endpoint {0} check timeout.'.format(host))
                    session_link.close()

                else:
                    session_link.post_alive_pkt()#心跳
                    session_link.get_status()#错误状态
                    #获取状态
                    ret = session_link.agv_status()
                    if ret < 0:
                        print('mt---get robot ', key_item, 'error failed')
                    else:
                        if self.__agv_status[key_item] == ret:
                            pass
                        else:
                            self.__agv_status[key_item] = ret
                            global mt_status_notify
                            if mt_status_notify is not None:
                                mt_status_notify(key_item,self.__agv_status[key_item])
            sleep(2)

    def remove_robot_id(self,robot_id):
        self.__mutex.acquire()
        if robot_id in self.__robot_lnk.keys():
            del (self.__robot_lnk[robot_id])
            del (self.__agv_status[robot_id])
            print('success remove mt robot id:', robot_id)
        self.__mutex.release()

    def get_var(self,id):
        if self.__robot_lnk.__contains__(id) == False:
            return {},-1
        self.__mutex.acquire()
        session_link=self.__robot_lnk[id]
        self.__mutex.release()
        pkt_id=session_link.get_var_list()
        valid_list=list()
        if wait_handler().wait_simulate(pkt_id, 5000) >=0:
            var_list=session_link.get_local_var_list()
            wait_handler().wait_destory(pkt_id)
            valid_list = mt_var_info.get_valid_list(var_list)
        else :return {},-2
        return valid_list,0

    def robots_status(self):
        status_list=dict()
        # self.__mutex.acquire()
        for robot_id in self.__robot_lnk.keys():
            status_list[int(robot_id)] = self.__agv_status[int(robot_id)]
        # self.__mutex.release()
        return status_list


    def var_data(self,id,var_id):
        if self.__robot_lnk.__contains__(id) == False:
            return {}
        self.__mutex.acquire()
        session_link=self.__robot_lnk[id]
        self.__mutex.release()

        pkt_id,type_id = session_link.get_var_data(var_id)
        if pkt_id==-1:
            return {}
        var_data = []
        if wait_handler().wait_simulate(pkt_id, 5000) >= 0:
            tmppp = session_link.get_local_var_data()
            wait_handler().wait_destory(pkt_id)
            var_data=mt_var_info.get_var_data(var_id,type_id,tmppp)
        return var_data

    def callback_error_status(self,notify_call=None):
        if notify_call is not None:
            global mt_status_notify
            mt_status_notify = notify_call

###############################################对外接口层#############################################

