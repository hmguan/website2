from pynsp.wait import *
from pynsp.logger import *
from .shell_manager import shell_manager
from agvinfo.dhcp_agent_center import agvinfoserver_online_robot,agvinfoserver_sh_closed,agvinfoserver_offline_robot
from .file_rw import *
import copy
import os

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
                        fiex_system_info = shell_manager().get_fixed_sysytem_info(item.id)
                        process_info = shell_manager().get_shell_process_detail_info(item.id)
                        list_progress = []
                        if process_info is not None:
                            for item in process_info:
                                list_progress.append({'process_name':item.get('process_name'),'status':(1 if (item.get('process_pid') > 0) else 0)})
                        notify_client_function({'msg_type':errtypes.TypeShell_NewArrival,'process_group':
                                                shell_manager().get_shell_process_name_join(item.id),'robot_id':item.id,
                                                'robot_host':item.host,'robot_mac':item.mac,'shell_time':'00:00:00',
                                                'shell_version':fiex_system_info.get('config_version'),'lock_status':fiex_system_info.get('lock_status'),
                                                'ntp_server':fiex_system_info.get('ntp_server'),
                                                'process_list':list_progress})
                    global_mutex.acquire()
                    if item.id in unusual_collection.keys():
                        del unusual_collection[item.id]
                    global_mutex.release()
                elif result < 0:
                    #记录连接不成功的异常
                    #连接异常时，直接从在线信息中删除
                    del_robot(item.id)
                    global_mutex.acquire()
                    if item.id not in unusual_collection.keys():
                        unusual_collection[item.id]={'robot_mac':item.mac,'robot_host':item.host}
                    global_mutex.release()
                    #通知前端
                    if notify_client_function is not None:
                        notify_client_function({'msg_type':errtypes.TypeShell_ConnectException,'robot_id':item.id,
                                                'robot_mac':item.mac,'robot_host':item.host})


#检测文件是否过期
def thread_check_file_expired():
    from time import sleep
    from configuration import system_config
    default_retention_time_min = 24*60
    default_time_intervel_sec = 10*60

    while is_exit_thread == False:
        retention_time_min = system_config.get('retention_time_min')
        if retention_time_min is None:
            retention_time_min = default_retention_time_min

        time_intervel_sec = system_config.get('time_intervel_sec')
        if time_intervel_sec is None:
            time_intervel_sec = default_time_intervel_sec

        path_config = system_config.get('path_element')

        if path_config is None:
            Logger().get_logger().error('No path_element configuration item was found')
            return

        for folder_path in path_config:
            walk_file(folder_path.get('path_root'),retention_time_min *60,folder_path.get('path_model'))

        sleep(time_intervel_sec)


def walk_file(root_path,retention_time,model=None):
    #文件夹不存在 或者 非文件夹路径
    if os.path.isdir(root_path) == False:
        return

    current_timestamp = int(round(time.time() * 1000))
    # files = os.listdir(filepath)
    # for file_name in files:
    #     fi_d = os.path.join(filepath,file_name)
    #     if os.path.isdir(fi_d):
    #         walk_file(fi_d)
    #     else:
    #         print os.path.join(filepath,fi_d)

    for root,dirs,files in os.walk(root_path,True):
        if root != root_path and model is not None:
            dirs[:] = list(set(dirs).intersection(set(model)))
        for file_name in files:
            file_path = os.path.join(root, file_name)
            last_update_file = os.path.getmtime(file_path)
            if last_update_file >= current_timestamp :
                continue
            elif (current_timestamp - last_update_file) > retention_time:
                if skip_file(file_name) is not False:
                    Logger().get_logger().info('remove file:filename{}'.format(file_path))
                    os.remove(file_path)


def skip_file(filename) ->bool:
    return False


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
    
    print('start remove global robot info')
    mac_addr = del_robot(robot_id)
    if len(mac_addr) == 0:
        print('-----remote robot mac address is empty-----')
        return
    #通知dhcp有车下线
    print('offline robot mac:',mac_addr)
    agvinfoserver_sh_closed(mac_addr)

def del_robot(robot_id):
    global global_mutex
    global_mutex.acquire()
    for key,item in global_robot_info.items():
        if item.id == robot_id:
            del (global_robot_info[key])
            global_mutex.release()
            print('success delete global robot info of key:',key)
            return key
    global_mutex.release()
    return ''

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
    (shelltime,versionifno,process_list,system_info,process_info) = shell_manager().get_all_robot_online_info()
    for mac_key,item in global_robot_info.items():
        process = process_list.get(item.id)
        list_progress = []
        if process_info is not None:
            for item in process_info.get(item.id):
                list_progress.append({'process_name':item.get('process_name'),'status':(1 if (item.get('process_pid') > 0) else 0)})

        robot_info = {'robot_id':item.id,'robot_mac':mac_key,'robot_host':item.host,
                      'shell_time':shelltime.get(item.id),'shell_version': versionifno.get(item.id),
                      'lock_status':system_info.get('lock_status'),
                      'ntp_server':system_info.get('ntp_server'),
                      'process_list':list_progress}
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
    shell_manager().register_socket_io_notify(notify_call)

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


def cancle_file_transform(user_id, robot_id, task_id_list) ->list:
    return file_manager().cancle_file_transform(user_id,robot_id,task_id_list)


def push_file_to_remote(user_id, robot_list, file_path, file_type,package_id):
    return file_manager().push_file_task(user_id, robot_list, file_path, file_type,package_id)

#route_path_list [{'robot_id':None ,'file_path':None,'local_path',None}]
#return 
def pull_file_from_remote(user_id,file_type,route_path_list=[]):
    return file_manager().pull_file_task(user_id,file_type,route_path_list)

def query_user_transmit_queue(user_id,oper_type)->list:
    return file_manager().query_transfer_queue(user_id,oper_type)

#传输文件过程中，回调函数中不能处理过长时间调用
def file_tansfer_notify(user_id, robot_id, file_path, file_type, step, error_code, status, task_id,file_size=0):
    from app.user.userview import users_center
    from app.soketio import socketio_agent_center
    from .shproto.errno import g_err_str
    global notify_client_function

    notify_dic = dict()
    notify_dic['user_id'] = user_id
    notify_dic['robot_id'] = robot_id
    notify_dic['file_path'] = file_path
    notify_dic['step'] = step
    notify_dic['error_code'] = error_code
    if error_code and error_code in g_err_str:
        notify_dic['error_msg'] = g_err_str[error_code]
    else:
        notify_dic['error_msg'] = ''
    notify_dic['status'] = status
    notify_dic['task_id'] = task_id

    # if step == 100:
#    print(step)
    u_uuid = users_center.user_uuid(user_id)
    if u_uuid is not None:
        if FILE_TYPE_A_UPGRADE == file_type :
            notify_dic['msg_type'] = errtypes.TypeShell_UpdateSoftware
            if 100 == step and status == 1:
                print("a begin upgrade")
                f_name = file_path[file_path.rfind('/') + 1:]
                shell_info = shell_manager().get_session_by_id(robot_id)
                if shell_info is not None:
                    shell_info.post_a_begin_upgrade(f_name, file_size)

            if notify_client_function is not None:
                notify_client_function(notify_dic)
            # sockio_api.response_to_client_data(notify_dic)
            # socketio_agent_center.post_msg_to_room(notify_dic,room_identify=u_uuid)
        elif FILE_TYPE_VCU_UPGRADE == file_type and 100 == step:
            pass
        elif FILE_TYPE_BLACKBOX_PULL_FILES == file_type:
            global step_notify_callback
            print('pull', step_notify_callback,step)
            if step_notify_callback is not None:
                step_notify_callback(user_id,robot_id, step, file_path, error_code)
        else:
            pass

def register_notify_log_step(notify_call=None):
    if notify_call is not None:
        global step_notify_callback
        step_notify_callback=notify_call

def get_robot_list_basic_info():
    from copy import deepcopy
    group_robot_info = {}
    robots_info_list = deepcopy(shell_manager().get_robots_configuration_info())
    for (robot_id,robot_info) in robots_info_list.items():
        process_name = robot_info.get('process_list')
        system_info = robot_info.get('system_info')
        if process_name is None or system_info is None:
            continue

        if process_name not in group_robot_info:
            group_robot_info[process_name] = {'robot_list':[]}
        group_robot_info[process_name].get('robot_list').append({'robot_id':robot_id,
                                                                'robot_host':robot_info.get('robot_host'),
                                                                'lock_status':system_info.get('lock_status'),
                                                                'ntp_server':system_info.get('ntp_server')
                                                                })
    return group_robot_info

def modify_robot_file_lock(robot_list,opecode) ->list:
    error_list = list()
    for robot_id in robot_list:
        if shell_manager().modify_robot_file_lock(robot_id,opecode) != 0:
            error_list.append(robot_id)
    return error_list

def update_ntp_server(robot_list,ntp_host) ->list:
    error_list = list()
    for robot_id in robot_list:
        if shell_manager().update_robot_ntp_server(robot_id,ntp_host) != 0:
            error_list.append(robot_id)
    return error_list

def query_progress_list():
    from copy import deepcopy
    robots_progress_list = dict()
    dict_progress_info = deepcopy(shell_manager().Query_robots_progress_list())
    for (robot_id,robot_info) in dict_progress_info.items():
        process_name = robot_info.get('process_list')
        progress_info = robot_info.get('progress_info')

        if process_name is None or progress_info is None:
            continue

        if process_name not in robots_progress_list:
            robots_progress_list[process_name] = {'robot_list':[]}
        list_progress = []
        for item in progress_info:
            list_progress.append({'process_name':item.get('process_name'),'status':(1 if (item.get('process_pid') > 0) else 0)})
        robots_progress_list[process_name].get('robot_list').append({'robot_id':robot_id,
                                                                    'progress_list':list_progress
                                                                    })
    return robots_progress_list

def setting_progress_state(robot_list,command):
    return shell_manager().setting_progress_state(robot_list,command)