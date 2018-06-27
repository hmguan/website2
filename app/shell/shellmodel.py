from agvshell.shell_api import *
from pynsp.logger import *
from ..user.userview import users_center
import errtypes

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

def query_transmit_queue( userid ):
    from db.db_package import package_manager
    if type(userid) != int:
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}
    try:
        transfer_queue = query_user_transmit_queue(userid)
        file_info = {}
        err_info = {}
        packet_info = None
        for item in transfer_queue:
            packet_info = file_info.get(item['packet_id'])
            if packet_info is None and item['packet_id'] not in err_info:
                packet_info = package_manager.query_packages(item['packet_id'])
                if packet_info is None:
                    err_info[item['packet_id']] = None
                    continue
            item['file_name'] = packet_info.package_name
            item['version'] = packet_info.version
            item['author'] = packet_info.user.username
        return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'transfer_list': transfer_queue}
    except Exception as e:
        return {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}



