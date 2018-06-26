# -*- coding: utf-8 -*-

from agvshell import shell_session, file_rw
from pynsp import singleton as slt
from time import sleep
import threading
import time
import copy
from .shproto import proto_typedef as typedef
from .shproto.errno import *
from pynsp.logger import *
from pynsp.waite_handler import *

#监测心跳超时时间戳差
CHECK_ALIVE_TIMESTAMP_OUT=6000

@slt.singleton
class shell_manager():
    def __init__(self):
        self.__robot_lnk={}
        self.__is_exist_th=False
        self.__mutex=threading.RLock()
        self.__check_timeout=threading.Thread(target=shell_manager.check_session_timeout,args=(self,))
        self.__check_timeout.setDaemon(True)
        self.__check_timeout.start()
        pass

    def __del__(self):
        self.__is_exist_th=True
        self.__check_timeout.join()
        pass

    def login_to_shell(self,robot_id,ipv4,port,notify_callback = None)->int:
        '''
        login to agvshell robot,while login failed ,it will not push current session link
        in to robot link collection.
        :param robot_id: int value
        :param ipv4: target robot endpoint,e.g.,192.168.0.1
        :param port:target robot prt,e.g.,4409
        :return:-1:login failed,0:login success,1:has already login
        '''
        if self.__robot_lnk.__contains__(robot_id) == True:
            Logger().get_logger().warning("the robot id {0} is already connected.".format(robot_id))
            return 1

        session_link = shell_session.shell_session(notify_closed = notify_callback, notify_file_manager = file_rw.file_manager())
        if session_link.try_connect(ipv4,port,robot_id) < 0:
            return -1

        for index in range(0,50):
            if session_link.get_network_status() == typedef.NetworkStatus_Ready:
                if session_link.try_login() < 0:
                    Logger().get_logger().error('failed to login target endpoint:{0} robot id:{1}'.format(ipv4,robot_id))
                    return -1
                else:
                    #请求获取车辆基本信息,此处同步等待接口
                    pkt_id = session_link.post_sysinfo_fixed_request()
                    if pkt_id < 0:
                        Logger().get_logger().error("failed post sysinfo fixed request to agvshell.")
                        break
                    #同步等待
                    if wait_handler().wait_simulate(pkt_id,3000) >= 0:
                        wait_handler().wait_destory(pkt_id)
                    break
            else:
                Logger().get_logger().warning("wait for pre login pakcage.")
                sleep(0.1)

        self.__mutex.acquire()
        self.__robot_lnk[robot_id] = session_link
        self.__mutex.release()
        return 0

    def check_session_timeout(self):
        '''
        the thread of check local session link is timeout or not.
        it also post alive package to all online robot
        :return:
        '''
        while self.__is_exist_th == False:
            self.__mutex.acquire()
            keys = list(self.__robot_lnk.keys())
            current_timestamp = int(round(time.time() * 1000))

            # 文件传输超时检测
            #Logger().get_logger().info('start file manager check timeout,current timestamp:{0}'.format(current_timestamp))
            file_rw.file_manager().check_file_timeout(current_timestamp)
            #Logger().get_logger().info('end file manager check timeout')

            for key_item in keys:
                # if self.__robot_lnk[key_item] is not None:
                host = self.__robot_lnk[key_item].get_host_ipv4()
                if (current_timestamp - self.__robot_lnk[key_item].get_timestamp()) > CHECK_ALIVE_TIMESTAMP_OUT:
                    #超时，则直接关闭连接
                    Logger().get_logger().error('the target endpoint {0} check timeout,current timestamp:{1},session timestamp:{2}.'.format(host,
                                                                                                                                            current_timestamp,
                                                                                                                                            self.__robot_lnk[key_item].get_timestamp()))
                    print("shell manager check timeout thread id:",threading.current_thread().ident," thread name:",threading.current_thread().name)
                    self.__robot_lnk[key_item].close()
                else:
                    if self.__robot_lnk[key_item].post_alive_pkt() < 0:
                        self.__robot_lnk[key_item].close()

            self.__mutex.release()
            sleep(2)

    def get_online_robot(self):
        self.__mutex.acquire()
        ls_value=self.__robot_lnk.keys()
        self.__mutex.release()
        return ls_value

    def remove_robot_id(self,robot_id):
        Logger().get_logger().warning('remove manager robot id:{0}'.format(robot_id))
        self.__mutex.acquire()
        if robot_id in self.__robot_lnk.keys():
            del(self.__robot_lnk[robot_id])
            print('success remove robot id:',robot_id)
        self.__mutex.release()

    def get_shell_service_info(self,robot_id):
        info = {}
        self.__mutex.acquire()
        if robot_id in self.__robot_lnk.keys():
            info = self.__robot_lnk.get(robot_id).get_shell_sys_service_info()
        self.__mutex.release()
        return info

    def get_all_robot_online_info(self):
        '''
        get all online robot information,it contails version info,
        connected time info,agv shell manager process list info
        :return:shell connected time dict,version dict,process list dic
        '''
        shtime_info = dict()
        version_info = dict()
        process_list = dict()

        self.__mutex.acquire()
        keys = list(self.__robot_lnk.keys())
        for key in keys:
            shtime_info[key] = self.__robot_lnk.get(key).get_connectedtime_value()
            version_info[key] = self.__robot_lnk.get(key).get_shell_version()
            process_list[key] =self.__robot_lnk.get(key).get_shell_process_list()
        self.__mutex.release()
        #key:robot id
        return shtime_info,version_info,process_list
        
    def get_session_by_id(self,robot_id):
        return self.__robot_lnk.get(robot_id)
    
    def get_fixed_sysytem_info(self,robot_id)->dict:
        info = dict()
        self.__mutex.acquire()
        if robot_id in self.__robot_lnk.keys():
            info = self.__robot_lnk.get(robot_id).get_fixed_system_info()
        self.__mutex.release()
        return info

    def get_shell_process_name_join(self,robot_id):
        result = ''
        self.__mutex.acquire()
        if robot_id in self.__robot_lnk.keys():
            result = self.__robot_lnk.get(robot_id).get_shell_process_list()
        self.__mutex.release()
        return result

    def get_shell_process_detail_info(self,robot_id)->list:
        info = list()
        self.__mutex.acquire()
        if robot_id in self.__robot_lnk.keys():
            info = self.__robot_lnk.get(robot_id).get_shell_process_detail_list()
        self.__mutex.release()
        return info