from .agvinfoser import *
from .agvinfotrs import *

notify_function_list=[]

def regist_agvinfo_notify(notify=None):
    '''
    register notification callback function,
    while get dhcp changed,it will callback the regist fucntion.
    :param notify:
    :return:
    '''
    if notify is not None:
        notify_function_list.append(notify)

def dhcp_notify_change():
    '''
    the agvinfo server changed,then notify local regist fucntion,
    the regist function will get all robot information
    :return:
    '''
    print('get agvinfoserver changed')
    for item in notify_function_list:
        item()

def agvinfoserver_online_robot():
    '''
    get online robot collection
    :return:
    '''
    return agvinfoser_getagvs()

def agvinfoserver_offline_robot():
    '''
    get offline robot collection
    :return:
    '''
    return agvinfoser_getoffline()

def agvinfoserver_sh_closed(mac_address):
    '''
    notify agvinfoserver someone robot offline
    :param mac_address:
    :return:
    '''
    return agvinfoser_shclosed(mac_address)

def agvinfoserver_mt_closed(mac_address):
    '''
    notify agvinfoserver mt link is closed
    :param mac_address:
    :return:
    '''
    return agvinfoser_mtclosed(mac_address)

def start_agvinfo_service():
    '''
    start agvinfo server,the server will report online robot collection information
    :return:
    '''
    #regist_agvinfo_notify(notify = dhcp_online_change)
    #agvinfoser_startup(_notify_changed=dhcp_notify_change)
    #agvinfotrs_startup()