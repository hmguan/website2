#from agvmt.mt_api import register_browser_mt_notify,start_connect_to_mt_th,dhcp_notify_change
import threading

# 启动mt本地管理
def start_mt_manager():
    '''
    start mt manager,the manager will start a new thread
    and regist notification to agvinfo
    :return:
    '''
    #注册给agvinfo(dhcp)模块有上下线通知
    from agvmt.mt_api import start_connect_to_mt_th,dhcp_notify_change
    from agvinfo.dhcp_agent_center import regist_agvinfo_notify
    regist_agvinfo_notify(notify=dhcp_notify_change)
    st = threading.Thread(target=start_connect_to_mt_th)
    st.start()


def register_mt_notify_function(notify_call=None):
    '''
    regist notification of browser,while session get some data changed,
    it will push data to browser via socketio
    :param notify_call:
    :return:
    '''
    from agvmt.mt_api import register_browser_mt_notify
    register_browser_mt_notify(notify_call)