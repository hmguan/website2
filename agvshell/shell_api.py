from pynsp.wait import *
from pynsp.logger import *
from .shell_manager import shell_manager
from agvinfo.dhcp_agent_center import agvinfoserver_online_robot,agvinfoserver_sh_closed,agvinfoserver_offline_robot
from .file_rw import *
import copy

#全局在线机器人信息
global_robot_info=dict()
#全局数据锁
global_mutex=threading.RLock()
#全局通知函数,回调至用户层，由用户层分发至浏览器
notify_client_function=None
#全局线程退出标识
is_exit_thread=False
#线程等待新车上线信号
thread_wait = waitable_handle(True)
#新车上线字典，每次连接成功一个车会弹出一个
robot_collection=dict()
#未连接成功的车
unusual_collection=dict()   #key:robot id ,value:{mac_address:xxxxxxxx,host:xxxxxxxxx}

#循环连车线程
def start_connect_to_robot():
    '''
    this thread used for connect to robot loop,while the online robot list has new value,
    it will get value and then connect to target endpoint.
    while connect over,online robot list will delete this one item.
    :return:
    '''
    while True:
        global thread_wait
        if (thread_wait.wait(0xffffffff) == False):
            pass
        if is_exit_thread == True:
            break

        while True:
            global robot_collection
            if len(robot_collection) == 0:
                break
            print('-----robot_collection:',robot_collection)
            all_keys = list(robot_collection.keys())
            global global_mutex
            for key in all_keys:
                global_mutex.acquire()
                item = robot_collection.get(key)
                del robot_collection[key]
                global_mutex.release()

                Logger().get_logger().info('get dhcp server notify,start to connect to {0}'.format(item.host))
                result = shell_manager().login_to_shell(item.id, item.host, item.shport.value,remote_robot)
                global notify_client_function
                if result == 0:
                    #新的客户端登录成功，则通知浏览器
                    if notify_client_function is not None:
                        notify_client_function({'msg_type':errtypes.TypeShell_NewArrival,'process_group':
                                                shell_manager().get_shell_process_name_join(item.id),'robot_id':item.id,
                                                'robot_host':item.host,'robot_mac':item.mac,'shell_time':'00:00:00'})
                    global_mutex.acquire()
                    if item.id in unusual_collection.keys():
                        del unusual_collection[item.id]
                    global_mutex.release()
                elif result < 0:
                    #记录连接不成功的异常
                    global_mutex.acquire()
                    if item.id not in unusual_collection.keys():
                        unusual_collection[item.id]={'robot_mac':item.mac,'robot_host':item.host}
                    global_mutex.release()
                    #通知前端
                    if notify_client_function is not None:
                        notify_client_function({'msg_type':errtypes.TypeShell_ConnectException,'robot_id':item.id,
                                                'robot_mac':item.mac,'robot_host':item.host})


#切换线程进行登录，不适用回调函数上来的线程，在调试过程中发现不切换线程时，容易造成登录agv_shell超时
def agvinfo_notify_change():
    info = agvinfoserver_online_robot()

    global global_mutex
    global_mutex.acquire()
    global global_robot_info,robot_collection
    global_robot_info.clear()
    global_robot_info=copy.deepcopy(info)
    print('----------dhcp notify changed global_robot_info:',global_robot_info)
    for key,item in global_robot_info.items():
        if robot_collection.__contains__(key) == False:
            robot_collection[key]=item

    global_mutex.release()
    del info
    global thread_wait
    thread_wait.sig()

#远端车下线通知
def remote_robot(robot_id):
    print("remote robot thread id:", threading.current_thread().ident," thread name:",threading.current_thread().name)
    shell_manager().remove_robot_id(robot_id)
    #通知客户端车辆断线变更,构造json格式
    global notify_client_function
    if notify_client_function is not None:
        notify_client_function({'msg_type':errtypes.TypeShell_Offline,'robot_id':robot_id})
    #删除global_robot_info中对应机器人信息
    mac_addr = ''
    print('start remove global robot info')
    global global_mutex
    global_mutex.acquire()
    print('global_robot_info:',global_robot_info)
    for key,item in global_robot_info.items():
        if item.id == robot_id:
            mac_addr = key
            del (global_robot_info[key])
            print('success delete global robot info of key:',key)
            break

    global_mutex.release()
    if len(mac_addr) == 0:
        print('-----remote robot mac address is empty-----')
        return
    #通知dhcp有车下线
    print('offline robot mac:',mac_addr)
    agvinfoserver_sh_closed(mac_addr)


###############################################对外接口层，用户提供外部调用#############################################

def get_online_robot_list():
    '''
    get all online robot list information
    :return:dict of group detail info
    {'process_group_name':[{robot_id:1,robot_mac:'xxxxxx',robot_host:'192.168.0.1',
    'shell_time':'00:00:10','shell_version':'v1.1.0'},{......},{......}]}
    '''
    group_robot_info = {}
    global global_mutex
    global_mutex.acquire()
    (shelltime,versionifno,process_list) = shell_manager().get_all_robot_online_info()
    for mac_key,item in global_robot_info.items():
        process = process_list.get(item.id)
        robot_info = {'robot_id':item.id,'robot_mac':mac_key,'robot_host':item.host,
                      'shell_time':shelltime.get(item.id),'shell_version': versionifno.get(item.id)}
        if process not in group_robot_info.keys():
            group_list = list()
            group_list.append(robot_info)
            group_robot_info[process] = group_list
        else:
            value = [group_item for group_item in group_robot_info[process] if mac_key == group_item.get('robot_mac') ]
            if len(value) == 0:
                group_robot_info[process].append(robot_info)
    global_mutex.release()
    return group_robot_info

def get_offline_robot_list():
    '''
    get all offline robot information,
    it will retrun robot id,robot mac address,robot ipv4
    :return:[{robot_id:1,robot_mac:xxxxxxxxxxxxxxx,robot_host:'192.168.0.1'},{......},{......}]
    '''
    offline_info = agvinfoserver_offline_robot()
    info_list = list()
    for item in offline_info:
        info_list.append({'robot_id':item.vhid,'robot_mac':item.hwaddr,'robot_host':item.inet})
    return info_list

def get_unusual_robot_list():
    '''
    get all unusual robot information,
    it will return the robot which can not connected.
    :return: [{robot_id:1,robot_mac:xxxxxxxxxxxxxxx,robot_host:'192.168.0.1'},{......},{......}]
    '''
    global global_mutex
    global_mutex.acquire()
    info_list = list()
    for keys,item in unusual_collection.items():
        info_list.append({'robot_id':keys,'robot_mac': item.get('robot_mac'),'robot_host':item.get('robot_host')})
    global_mutex.release()
    return info_list

def register_browser_notify(notify_call=None):
    '''
    register browser notification
    :param notify_call:
    :return:
    '''
    if notify_call is not None:
        global notify_client_function
        notify_client_function=notify_call

def get_robot_detail_info(robot_id):
    '''
    get robot detail information,it contains robot memory,
    CPU,system information and so on.
    :param robot_id:
    :return:
    '''
    detail_info = shell_manager().get_fixed_sysytem_info(robot_id)
    global global_mutex
    global_mutex.acquire()
    global global_robot_info
    mac_list = [item.mac for item in global_robot_info.values() if item.id == robot_id]
    detail_info['robot_mac'] = mac_list[0] if len(mac_list) != 0 else ""
    global_mutex.release()
    return detail_info

def get_robot_system_info(robot_id):
    '''
    get robot system information while running.
    :param robot_id:
    :return:
    '''
    return shell_manager().get_shell_service_info(robot_id)

def get_robot_process_detail_info(robot_id):
    '''
    get robot process detail information
    :param robot_id:
    :return:
    '''
    return shell_manager().get_shell_process_detail_info(robot_id)

def change_pull_file_dir(path):
    file_manager().change_file_dir(path)


def change_file_block_size(size):
    file_manager().change_block_size(size)


def cancle_file_transform(session_uid, robot_id, file_path):
    file_manager().cancle_file_transform(session_uid, robot_id, file_path)


def push_file_to_remote(session_uid, robot_list, file_path, file_type):
    file_manager().push_file_task(session_uid, robot_list, file_path, file_type)

def pull_file_from_remote(session_uid, robot_list, file_path, file_type):
    file_manager().pull_file_task(session_uid, robot_list, file_path)

current_step = 0
def file_tansfer_notify(session_uid, robot_id, file_path, file_type, step, error_code, status, file_size=0):
    notify_dic = dict()
    notify_dic['type'] = errtypes.TypeShell_UpdateSoftware
    notify_dic['session_uid'] = str(session_uid).encode('utf-8')
    notify_dic['robot_id'] = robot_id
    notify_dic['file_path'] = file_path
    notify_dic['step'] = step
    notify_dic['error_msg'] = error_code
    notify_dic['status'] = status

    # if step == 100:
    global current_step
    value = int(float(step))
    if status != 0 or current_step != value:
        current_step = value
        global notify_client_function
        if notify_client_function is not None:
            notify_client_function(notify_dic)

    if FILE_TYPE_A_UPGRADE == file_type and 100 == step:
        print("a begin upgrade")
        f_name = file_path[file_path.rfind('/') + 1:]
        shell_info = shell_manager().get_session_by_id(robot_id)
        if shell_info is not None:
            shell_info.post_a_begin_upgrade(f_name, file_size)
        pass
    elif FILE_TYPE_VCU_UPGRADE == file_type and 100 == step:
        pass
    else:
        pass