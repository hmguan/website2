import threading
from agvmt.mt_manage import mt_manage
from pynsp.wait import *
import copy
from agvinfo.dhcp_agent_center import regist_agvinfo_notify,agvinfoserver_online_robot,agvinfoserver_mt_closed
import errtypes
from agvinfo import agvinfoser
from time import sleep

#mt_status_notify=None
#全局数据锁
global_mt_mutex=threading.RLock()
#全局线程退出标识
is_exit_mt_thread=False
#线程等待新车上线信号
mt_thread_wait = waitable_handle(True)
mt_collection = dict()
#全局在线机器人信息
mt_robot_info=dict()

def dhcp_notify_change():
    agv_info = agvinfoserver_online_robot()
    #start_connect_to_mt(info)
    global global_mt_mutex
    global_mt_mutex.acquire()
    global mt_collection
    global mt_robot_info
    mt_robot_info.clear()
    mt_robot_info = copy.deepcopy(agv_info)
    for key,item in mt_robot_info.items():
        if key not in mt_collection.keys():
            mt_collection[key] = item
    global_mt_mutex.release()
    del agv_info
    global mt_thread_wait
    mt_thread_wait.sig()

    mt_manage().callback_error_status(get_mt_error)

def start_connect_to_mt_th():
    '''
    this thread used for connect to robot loop,while the online robot list has new value,
    it will get value and then connect to target endpoint.
    while connect over,online robot list will delete this one item.
    :return:
    '''
    # print('start')
    # info = agvinfoser.agvinfo_runtime(1, '10.10.100.131', 4409, 'aa:bb:cc', 4410)
    # mt_manage().login_to_mt(info.id, info.host, info.shport, remote_robot, )
    while True:
        global mt_thread_wait
        if (mt_thread_wait.wait(0xffffffff) == False):
            pass
        if is_exit_mt_thread == True:
            break
        while True:
            global mt_collection
            if len(mt_collection) == 0:
                break
            print('mt_collection:',mt_collection)
            all_keys = list(mt_collection.keys())
            global global_mt_mutex
            for key in all_keys:
                global_mt_mutex.acquire()
                item = mt_collection[key]
                del mt_collection[key]
                global_mt_mutex.release()
                if item.mtready:
                    print('mt-ready',item.mtready)
                    mt_manage().login_to_mt(item.id, item.host, item.shport,remote_robot,)

#agvinfoser下线通知
def remote_robot(robot_id):
    mt_manage().remove_robot_id(robot_id)
    #通知客户端车辆断线变更,构造json格式
    global notify_client_function
    if notify_client_function is not None:
        notify_client_function({'msg_type':errtypes.TypeMT_Offline,'robot_id':robot_id})
    mac_addr = ''
    print('start remove mt robot info')
    #删除全局在线mt
    global global_mt_mutex
    global_mt_mutex.acquire()
    for key,item in mt_robot_info.items():
        if item.id == robot_id:
            mac_addr = key
            del (mt_robot_info[key])
            print('success delete mt robot info of key:',key)
            break

    global_mt_mutex.release()
    if len(mac_addr) == 0:
        print('-----remote mt robot mac address is empty-----')
        return
    #通知agvifoser有车下线
    print('offline mt mac:',mac_addr)
    agvinfoserver_mt_closed(mac_addr)

def clear_error(robot_list):
    mt_manage().clear_agv_error(robot_list)

def get_nav_data(robot_id):
    return mt_manage().get_navigation_data(robot_id)

def get_veh_data(robot_id):
    return mt_manage().get_vehicle_data(robot_id)

def get_ope_data(robot_id):
    return mt_manage().get_operation_data(robot_id)

def get_opt_data(robot_id):
    return mt_manage().get_optpar_data(robot_id)

def set_stop_emergency(robot_list):
    mt_manage().set_stop(robot_list)

def get_var_list(robot_id):
    return mt_manage().get_var(robot_id)

def get_vars_data(robot_id,var_id,type_id):
    return mt_manage().var_data(robot_id,var_id,type_id)

def get_robots_status():
    return mt_manage().robots_status()

def register_browser_mt_notify(mt_notify=None):
    global notify_client_function
    notify_client_function = mt_notify

def get_mt_error(robot_id, status):
    print('get mt error,robot id:{0},status:{1}'.format(robot_id, status))
    notify_dic = dict()
    notify_dic['msg_type'] = errtypes.TypeMT_Error
    notify_dic['robot_id'] = robot_id
    notify_dic['status'] = status
    global notify_client_function
    if notify_client_function is not None:
        notify_client_function(notify_dic)

##################################################################################
#自测部分

# def start_connect_to_mt(agv_info):
#     global global_mt_mutex
#     global_mt_mutex.acquire()
#     global mt_collection
#     global mt_robot_info
#     mt_robot_info.clear()
#     mt_robot_info = copy.deepcopy(agv_info)
#     for key,item in agv_info.items():
#         if key not in mt_collection.keys():
#             mt_collection[key] = item
#     global_mt_mutex.release()
#     global mt_thread_wait
#     mt_thread_wait.sig()
#
# def set_agv_info(agvinfo):
#     st = threading.Thread(target=start_connect_to_mt_th)
#     st.start()
#     start_connect_to_mt(agvinfo)
#
#if __name__ == '__main__':
#     print('1111111111')
#     info = agvinfoser.agvinfo_runtime(1, '10.10.100.131', 4409, 'aa:bb:cc', 4410)
#     infos = {'aa:bb:cc': info}
#     set_agv_info(infos)
#     sleep(2)
#     #set_stop_emergency(1)
#     #get_opt_data(1)
#     #get_nav_data(1)
#
#     get_nav_data(1)
#
#     sleep(2)
#     #get_vars_data(1, 131, 258)
#     get_vars_data(1, 1, 2)
#
#     get_var_list(1)
#     #get_vars_data(1,131,258)
#
#     sleep(2)
#     get_vars_data(1,102,260)
#     while 1:
#         print('---------')
#         sleep(2)