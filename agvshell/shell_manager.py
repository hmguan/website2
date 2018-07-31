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
from .notify_thread_socket_io import *

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
        self.__notify_thread = notify_thread()
        pass

    def __del__(self):
        self.__is_exist_th=True
        self.__check_timeout.join()
        del self.__notify_thread
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

        session_link = shell_session.shell_session(notify_closed = notify_callback, notify_file_manager = file_rw.file_manager(),push_notify=self.push_notify)
        if session_link.try_connect(ipv4,port,robot_id) < 0:
            return -1

        for index in range(0,50):
            if session_link.get_network_status() == typedef.NetworkStatus_Ready:
                if session_link.try_login() < 0:
                    Logger().get_logger().error('failed to login target endpoint:{0} robot id:{1}'.format(ipv4,robot_id))
                    session_link.close()
                    return -1
            elif session_link.get_network_status() == typedef.NetworkStatus_Established:
                # 请求获取车辆基本信息,此处同步等待接口
                pkt_id = session_link.post_sysinfo_fixed_request()
                if pkt_id < 0:
                    Logger().get_logger().error("failed post sysinfo fixed request to agvshell.")
                    break
                # 同步等待
                if wait_handler().wait_simulate(pkt_id, 3000) >= 0:
                    wait_handler().wait_destory(pkt_id)
                    session_link.post_request_process_config_list()
                break
            elif session_link.get_network_status() == typedef.NetworkStatus_Connected:
                Logger().get_logger().warning("wait for login package result ack.")
                sleep(0.1)
            else:
                Logger().get_logger().warning("wait for pre login pakcage.")
                sleep(0.1)

        if session_link.get_network_status() != typedef.NetworkStatus_Established:
            Logger().get_logger().error('failed to login target endpoint:{0} robot id:{1},then close the session'.format(ipv4,robot_id))
            session_link.close()
            return -1

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
            # 文件传输超时检测
            #Logger().get_logger().info('start file manager check timeout,current timestamp:{0}'.format(current_timestamp))
            file_rw.file_manager().check_file_timeout(int(round(time.time() * 1000)))
            #Logger().get_logger().info('end file manager check timeout')

            self.__mutex.acquire()
            keys = list(self.__robot_lnk.keys())
            self.__mutex.release()
            
            for key_item in keys:
                if self.__mutex.acquire() == True:
                    session_link = self.__robot_lnk.get(key_item)
                    self.__mutex.release()

                    if session_link is None:
                        continue

                    current_timestamp = int(round(time.time() * 1000))
                    host = session_link.get_host_ipv4()
                    session_time = session_link.get_timestamp()
                    if (current_timestamp - session_time) > CHECK_ALIVE_TIMESTAMP_OUT:
                        #超时，则直接关闭连接
                        Logger().get_logger().error('the target endpoint {0} check timeout,current timestamp:{1},session timestamp:{2},the interval timestamp:{3}'.format(host,
                                                                                                                                                current_timestamp,
                                                                                                                                                session_time,current_timestamp-session_time))
                        print("shell manager check timeout thread id:",threading.current_thread().ident," thread name:",threading.current_thread().name)
                        session_link.close()
                    else:
                        if session_link.post_alive_pkt() < 0:
                            Logger().get_logger().error('failed to post alive pkt to target endpoint:{0}'.format(host))
                            session_link.close()

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
        system_info = dict()
        self.__mutex.acquire()
        keys = list(self.__robot_lnk.keys())
        for key in keys:
            shtime_info[key] = self.__robot_lnk.get(key).get_connectedtime_value()
            version_info[key] = self.__robot_lnk.get(key).get_shell_version()
            process_list[key] =self.__robot_lnk.get(key).get_shell_process_list()
            system_info[key] = self.__robot_lnk.get(key).get_fixed_system_info()
        self.__mutex.release()
        #key:robot id
        return shtime_info,version_info,process_list,system_info

    def get_robots_configuration_info(self):
        robots_info = dict()

        self.__mutex.acquire()
        keys = list(self.__robot_lnk.keys())
        for key in keys:
            robots_info[key] ={'process_list':self.__robot_lnk.get(key).get_shell_process_list(),
                                'system_info':self.__robot_lnk.get(key).get_fixed_system_info(),
                                'robot_host':self.__robot_lnk.get(key).get_host_ipv4()}

        self.__mutex.release()
        return robots_info

        
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

    def push_notify(self,msg_type,data):
        if self.__notify_thread:
            self.__notify_thread.add_notify(msg_type,data)

    def register_socket_io_notify(self,socketio_notify):
        if self.__notify_thread:
            self.__notify_thread.register_socketio_notify(socketio_notify)

    def modify_robot_file_lock(self,robotid,opecode) ->int:
        err_code = 0
        try:
            self.__mutex.acquire()
            session = self.__robot_lnk.get(robotid)
            if session:
                session.post_modify_file_mutex(opecode)
            else:
                err_code = 1
            self.__mutex.release()
            return err_code
        except Exception as e:
            self.__mutex.release()
            Logger().get_logger().error('modify_robot_file_lock :{}'.format(str(e)))
            return 1

    def update_robot_ntp_server(self,robot_id,ntp_server) ->int:
        err_code = 0
        try:
            self.__mutex.acquire()
            session = self.__robot_lnk.get(robot_id)
            if session:
                session.update_ntp_server(ntp_server)
            else:
                err_code = 1
            self.__mutex.release()
            return err_code
        except Exception as e:
            Logger().get_logger().error('update_robot_ntp_server :{}'.format(str(e)))
            self.__mutex.release()
            return 1

    def Query_robots_progress_list(self)->dict:
        progress_info = dict()

        self.__mutex.acquire()
        keys = list(self.__robot_lnk.keys())
        for key in keys:
            session = self.__robot_lnk.get(key)
            if session is None:
                continue

            fiex_system_info = session.get_fixed_system_info()
            process_list = list()
            if 'process_list' in fiex_system_info:
                process_list = [{"process_name":item.get('process_name'),"status":item.get('status')} for item in fiex_system_info.get('process_list')]
            
            progress_info[key] ={
                                'group_name':session.get_shell_process_list(),
                                'process_list':process_list,
                                'robot_host':session.get_host_ipv4()
                                }
        self.__mutex.release()
        return progress_info

    def setting_progress_state(self,robot_list,command)->list:
        err_list = list()
        try:
            self.__mutex.acquire()
            for robot_id in robot_list:
                session = self.__robot_lnk.get(robot_id)
                if session:
                    session.operate_system_process(command)
                else:
                    err_list.append(robot_id)
            self.__mutex.release()
            return err_list
        except Exception as e:
            self.__mutex.release()
            Logger().get_logger().error('setting_progress_state :{}'.format(str(e)))
            return err_list

    def query_robot_process_config_info(self,robot_id)->dict:
        process_list = dict()
        self.__mutex.acquire()
        session = self.__robot_lnk.get(robot_id)
        if session:
            process_list = {'process_list':session.get_shell_process_config_list()}
        self.__mutex.release()
        return process_list

    def update_process_config_info(self,robot_id,process_list):
        error_code = -1
        self.__mutex.acquire()
        session = self.__robot_lnk.get(robot_id)
        if session:
            error_code = session.update_process_config_info(process_list)
        self.__mutex.release()
        return error_code
        