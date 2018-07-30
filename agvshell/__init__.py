from .shell_manager import shell_manager
from .file_rw import *

#启动本地shell管理
def start_agvshell_manager():
    '''
    start agvshell manager,the manager will start a new thread
    and regist notification to agvinfo and regist notification
    to file rw class,this class will transfer file to remote.
    :return:
    '''
    #注册给agvinfo(dhcp)模块有上下线通知
    from agvinfo.dhcp_agent_center import regist_agvinfo_notify
    from .shell_api import agvinfo_notify_change, start_connect_to_robot, file_tansfer_notify,thread_check_file_expired
    regist_agvinfo_notify(notify = agvinfo_notify_change)
    st = threading.Thread(target = start_connect_to_robot)
    st.start()

    detection_thread = threading.Thread(target=thread_check_file_expired)
    detection_thread.setDaemon(True)
    detection_thread.start()

    #注册文件传输至shell端回调例程
    file_rw.file_manager().register_shell_manager(shell_manager())
    file_rw.file_manager().register_notify_changed(file_tansfer_notify)

def register_notify_function(notify_call=None):
    '''
    regist notification of browser,while session get some data changed,
    it will push data to browser via socketio
    :param notify_call:
    :return:
    '''
    from .shell_api import register_browser_notify
    register_browser_notify(notify_call)