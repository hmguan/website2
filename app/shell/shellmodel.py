from agvshell.shell_api import *
from pynsp.logger import *
from ..user.userview import users_center
from agvshell.transfer_file_types import *
import errtypes
import httpRequestCode

set_push_file_type = {FILE_TYPE_A_UPGRADE,FILE_TYPE_VCU_UPGRADE}
set_pull_file_type = {FILE_TYPE_BLACKBOX_PULL_FILES}

def get_online_robot_information(user_id):
    '''
    get online robot information models,
    this models will call shell_api of agvshell package function
    :return:
    '''
    if type(user_id) != int or user_id is None:
        return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament,'data':''}
    try:
        online_info = get_online_robot_list()
        data_list=list()
        for keys,item in online_info.items():
            alias_name_dict = users_center.group_alias(user_id,keys)
            if alias_name_dict['code']!=0:
                return {'code':alias_name_dict['code'],'msg':errtypes.HttpResponseMsg_InvaildParament,'data':''}

            if alias_name_dict['alias'] is '':
                data_list.append({'process_group':keys,'process_group_alias':'','robot_list':item})
            else:
                data_list.append({'process_group': keys, 'process_group_alias': alias_name_dict['alias'], 'robot_list': item})
        print('data list:',data_list)
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'data': data_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e),'data':''}

def get_offline_robot_information():
    '''
    get offline robot information models,
    this models will call shell_api of agvshell package fucntion
    :return:
    '''
    try:
        offline = get_offline_robot_list()
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'robot_list': offline}
    except Exception as e:
        Logger().get_logger().error("it has exception {0} while get offlie robot information ".format(e))
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e),'offline_robot_list':''}

def get_unusual_robot_information():
    '''
    call shell_api get unusual robot info function
    :return:dict value
    '''
    try:
        unusual_info = get_unusual_robot_list()
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'robot_list': unusual_info}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e),'data':''}

def get_robot_detail_information(robot_id):
    '''
    call shell_api get robot detail info function
    :param robot_id:
    :return:
    '''
    if type(robot_id) != int or robot_id is None:
        return {'code':errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament,'data':''}
    try:
        return {'code': errtypes.HttpResponseCode_Normal,'msg': errtypes.HttpResponseMsg_Normal,'data':get_robot_detail_info(robot_id)}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e),'data':''}

def get_robot_system_information(robot_id):
    '''
    call shell_api get robot system information function
    :param robot_id:
    :return:
    '''
    if type(robot_id) != int or robot_id is None:
        return {'code':errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament,'system_info':''}
    try:
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'system_info': get_robot_system_info(robot_id)}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e),'system_info':''}

def get_robot_process_detail_information(robot_id):
    '''
    call shell_api get robot process detail information function
    :param robot_id:
    :return:
    '''
    if type(robot_id) != int or robot_id is None:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament, 'process_info_list': ''}
    try:
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'process_info_list': get_robot_process_detail_info(robot_id)}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e),'process_info_list':''}

def query_transmit_queue( userid ,file_type):
    from db.db_package import package_manager

    if type(userid) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        transfer_queue =list()
        if file_type in set_push_file_type:
            transfer_queue = query_user_transmit_queue(userid,FILE_OPER_TYPE_PUSH)
        elif file_type in set_pull_file_type:
            transfer_queue = query_user_transmit_queue(userid,FILE_OPER_TYPE_PULL)
        else:
            return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}

        packet_dict = dict()
        packet_info = None
        for item in transfer_queue:
            if file_type == item['file_type'] and file_type in set_push_file_type:
                packet_info = packet_dict.get(item['packet_id'])
                if packet_info is None and item['packet_id'] not in packet_dict:
                    packet_info = package_manager.query_packages(item['packet_id'])
                    if packet_info is not None:
                        packet_dict[item['packet_id']] = packet_info
                item['file_name'] = 'invalid'
                item['version'] = 'invalid'
                item['author'] = 'invalid'
                if packet_info is not None:
                    item['file_name'] = packet_info.package_name
                    item['version'] = packet_info.version
                    item['author'] = packet_info.user.username
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'transfer_list': transfer_queue}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def cancle_transform(user_id, task_id_list):
    if type(user_id) != int or type(task_id_list) != list or len(task_id_list) == 0:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        remove_task_list = list(map(int,task_id_list))
        if len(set(remove_task_list)) != len(remove_task_list):
            return {'code': errtypes.HttpResponseCode_IDRepetition, 'msg': errtypes.HttpResponseMsg_IDRepetition}

        remove_list = cancle_file_transform(user_id,remove_task_list)
        err_task = [{task_id:errtypes.HttpResponseCode_TaskNotExist} for task_id in remove_task_list if task_id not in remove_list]
        if len(err_task) > 0:
             return {'code': errtypes.HttpResponseCode_TaskNotExist, 'msg': errtypes.HttpResponseMsg_TaskNotExist,'err_task':err_task,'success':remove_list}
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal,'err_task':err_task,'success':remove_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}


def get_on_line_robot_configuration(user_id):
    if type(user_id) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}

    try:
        group_info = []
        robots_info = get_robot_list_basic_info()
        for (process_name,info) in robots_info.items():
            alias_name = users_center.group_alias(user_id,process_name)
            item_info = {'process_group':process_name,'process_group_alias':alias_name if alias_name else''}
            item_info.update(info)
            group_info.append(item_info)
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'data': group_info}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def modify_file_lock(opcode, robot_list):
    length_robots = len(robot_list)
    if type(opcode) != int or type(robot_list) != list or opcode not in {0,1} or length_robots == 0:
        return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
    robot_list = list(map(int,robot_list))    
    if len(set(robot_list)) != length_robots:
        return {'code': errtypes.HttpResponseCode_IDRepetition, 'msg': errtypes.HttpResponseMsg_IDRepetition}
    try:
        error_list = modify_robot_file_lock(robot_list,opcode)
        error_list = [{robot_id:errtypes.HttpResponseCode_RobotOffLine} for robot_id in error_list]
        if len(error_list) > 0:
            return {'code': errtypes.HttpResponseCode_RobotOffLine, 'msg': errtypes.HttpResponseMsg_RobotOffLine, 'error_list': error_list}
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'error_list': error_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def query_ftp_port():
    from configuration import config
    try:
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'ftp_port': config.HTTP_PORT,'websocket_port':config.WEBSOCKET_PORT}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def update_robots_ntp_server(robot_list,ntp_host):
    length_robots = len(robot_list)
    if type(robot_list) != list or type(ntp_host) !=str or length_robots == 0:
        return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
    robot_list = list(map(int,robot_list))
    if len(set(robot_list)) != length_robots:
        return {'code': errtypes.HttpResponseCode_IDRepetition, 'msg': errtypes.HttpResponseMsg_IDRepetition}
    try:
        robot_list = [int(robot_id) for robot_id in robot_list]
        error_list = update_ntp_server(robot_list,ntp_host)
        error_list = [{robot_id:errtypes.HttpResponseCode_RobotOffLine} for robot_id in error_list]
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'error_list': error_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}
    pass

def query_robots_progress_info(user_id):
    if type(user_id) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        group_info = []
        robots_info = query_progress_list()
        for (process_name,info) in robots_info.items():
            alias_name = users_center.group_alias(user_id,process_name)
            item_info = {'process_group':process_name,'process_group_alias':alias_name if alias_name else''}
            item_info.update(info)
            group_info.append(item_info)
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'data': group_info}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def operate_system_process(robot_list,command):
    length_robots = len(robot_list)
    if type(robot_list)!= list or type(command) != int or command not in {0,1,2} or length_robots == 0:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    robot_list = list(map(int,robot_list))
    if len(set(robot_list)) != length_robots:
        return {'code': errtypes.HttpResponseCode_IDRepetition, 'msg': errtypes.HttpResponseMsg_IDRepetition}
    try:
        error_list = setting_progress_state(robot_list,command)
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'error_list': error_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def query_robot_process_config_list(robot_id):
    if type(robot_id) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        process_info = query_robot_process_config_info(robot_id)
        if process_info:
            return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'process_list': process_info}
        return {'code': errtypes.HttpResponseCode_RobotOffLine, 'msg': errtypes.HttpResponseMsg_RobotOffLine}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def update_robot_process_config_list(robot_id,process_list):
    if type(robot_id) != int or type(process_list) != list:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        error_code = update_process_config_info(robot_id,process_list)
        if error_code == 0:
            return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal }
        return {'code': errtypes.HttpResponseCode_RobotOffLine, 'msg': errtypes.HttpResponseMsg_RobotOffLine}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def query_upgrade_file_write_permission(login_id,package_id):
    from db.db_package import package_manager
    from configuration import get_config_path

    if type(login_id) != int or type(package_id) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        retval = package_manager.query_packages(package_id)
        if retval is None:
            return {'code': errtypes.HttpResponseCode_DateBasePacketIdNotFound, 'msg': errtypes.HttpResponseMsg_DateBasePacketIdNotFound }

        user_name = retval.user.username
        package_name = retval.package_name
        file_path = get_config_path(user_name,httpRequestCode.HttpRequestFileType_Patch) + package_name

        if os.path.exists(file_path) is False:
            package_manager.remove(package_id)
            return {'code': errtypes.HttpResponseCode_DatabaseRecordAbnormity, 'msg': errtypes.HttpResponseMsg_DatabaseRecordAbnormity}

        if retval.user_id != login_id:
            return {'code': errtypes.HttpResponseCode_NotFileOwner, 'msg': errtypes.HttpResponseMsg_NotFileOwner}

        if os.access(file_path,os.W_OK) is False:
            return {'code': errtypes.HttpResponseCode_NoAuthority, 'msg': errtypes.HttpResponseMsg_NoAuthority}

        if is_file_open(file_path) or is_package_in_task(package_id):
            return {'code': errtypes.HttpResponseCode_FileBusy, 'msg': errtypes.HttpResponseMsg_FileBusy }

        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal }
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}


def query_upgrade_file_read_permission(login_id,package_id):
    from db.db_package import package_manager
    from configuration import get_config_path

    if type(login_id) != int or type(package_id) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        retval = package_manager.query_packages(package_id)
        if retval is None:
            return {'code': errtypes.HttpResponseCode_DateBasePacketIdNotFound, 'msg': errtypes.HttpResponseMsg_DateBasePacketIdNotFound }

        user_name = retval.user.username
        package_name = retval.package_name
        file_path = get_config_path(user_name,httpRequestCode.HttpRequestFileType_Patch) + package_name

        if os.path.exists(file_path) is False:
            package_manager.remove(package_id)
            return {'code': errtypes.HttpResponseCode_DatabaseRecordAbnormity, 'msg': errtypes.HttpResponseMsg_DatabaseRecordAbnormity}

        if retval.user_id != login_id:
            return {'code': errtypes.HttpResponseCode_NotFileOwner, 'msg': errtypes.HttpResponseMsg_NotFileOwner}

        if os.access(file_path,os.R_OK) is False:
            return {'code': errtypes.HttpResponseCode_NoAuthority, 'msg': errtypes.HttpResponseMsg_NoAuthority}

        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal }
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def robot_upgrade(package_id,user_id,robot_list):
    from db.db_package import package_manager
    from configuration import get_config_path
    
    if type(package_id) != int or type(robot_list) != list or type(user_id) != int or len(robot_list) == 0:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament }

    robot_list = list(map(int,robot_list))
    if len(set(robot_list)) != len(robot_list):
        return {'code': errtypes.HttpResponseCode_RobotIDRepetition, 'msg': errtypes.HttpResponseMsg_RobotIDRepetition }
    try:
        retval = package_manager.query_packages(package_id)
        if retval is None:
            return {'code': errtypes.HttpResponseCode_NOFILE, 'msg': errtypes.HttpResponseMsg_FileNotExist }

        user_name = retval.user.username
        package_name = retval.package_name
        file_path = get_config_path(user_name,httpRequestCode.HttpRequestFileType_Patch) + package_name
        if os.path.exists(file_path) == False:
            package_manager.remove(package_id)
            return {'code': errtypes.HttpResponseCode_DatabaseRecordAbnormity, 'msg': errtypes.HttpResponseMsg_DatabaseRecordAbnormity }
                
        error_code,task_list = push_file_to_remote(user_id,robot_list,file_path,FILE_TYPE_A_UPGRADE,package_id)
        if error_code == -1:
            return {'code': errtypes.HttpResponseCode_TaskFull, 'msg': errtypes.HttpResponseMsg_TaskFull }
        return {'code': 0,'msg':errtypes.HttpResponseMsg_Normal,'transfer_list':task_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}