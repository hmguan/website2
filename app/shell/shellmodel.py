from agvshell.shell_api import *
from pynsp.logger import *
from ..user.userview import users_center
from agvshell.transfer_file_types import *
import errtypes

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
            alias_name = users_center.group_alias(user_id,keys)
            if alias_name is None:
                data_list.append({'process_group':keys,'process_group_alias':'','robot_list':item})
            else:
                data_list.append({'process_group': keys, 'process_group_alias': alias_name, 'robot_list': item})
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
            pass

        packet_dict = dict()
        packet_info = None
        for item in transfer_queue:
            if file_type == item['file_type'] and file_type in set_push_file_type:
                packet_info = packet_dict.get(item['packet_id'])
                if packet_info is None and item['packet_id'] not in packet_dict:
                    packet_info = package_manager.query_packages(item['packet_id'])
                    if packet_info is not None:
                        packet_dict[item['packet_id']] = packet_info
                item['file_name'] = packet_info.package_name
                item['version'] = packet_info.version
                item['author'] = packet_info.user.username
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'transfer_list': transfer_queue}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}

def cancle_transform(user_id, robot_id, task_id_list):
    if type(user_id) != int or type(robot_id) != int or type(task_id_list) != list:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        remove_task_list = list()
        for task_id in task_id_list:
            if type(task_id) != int:
                task_id = int(task_id)
            remove_task_list.append(task_id)

        remove_list = cancle_file_transform(user_id,robot_id,remove_task_list)
        err_task = []
        for task_id in remove_task_list:
            if task_id not in remove_list:
                err_task.append(task_id)
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal,'err_task':err_task,'success':remove_list}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}


