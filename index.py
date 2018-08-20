from app import create_app
from agvinfo.dhcp_agent_center import start_agvinfo_service
from agvshell import start_agvshell_manager,register_notify_function
from agvmt import start_mt_manager,register_mt_notify_function
from pynsp.logger import *
import traceback
import sys
from backup import start_black_box,register_blackbox_step_notify_function
#import ptvsd
from configuration import config
from app.soketio.socketio_agent_center import *

#ptvsd.settrace(None, ('0.0.0.0', 12345))
# ptvsd.wait_for_attach()

app=create_app('default')

# 异常处理函数
def quiet_errors(exc_type, exc_value, tb):
    Logger().get_logger().error(''.join(traceback.format_exception(exc_type, exc_value, tb)))

# 定义全局异常捕获
sys.excepthook = quiet_errors

if __name__ == '__main__':
    try:
        web_port = config.WEB_PORT
        websocket_port = config.WEBSOCKET_PORT
    except Exception as e:
        web_port = 5008
        websocket_port = 5011

    #初始化日志文件
    init_logger()
    start_black_box()
    register_blackbox_step_notify_function(notify_call = send_msg_to_client_byuserid)
    #启动agvinfo server服务
    start_agvinfo_service()
    #启动agvshell manager管理服务
    start_agvshell_manager()
    #启动mt_manage管理服务
    start_mt_manager()
    #注册通知浏览器mt错误回调
    register_mt_notify_function(notify_call=send_msg_to_all)
    #注册通知浏览器回调例程
    register_notify_function(notify_call=send_msg_to_all)
    # 初始化websocket监听端口
    init_websocket(host='0.0.0.0', port=websocket_port)
    #启动socket io服务
    app.run(host='0.0.0.0', port=web_port, debug=True,use_reloader=False)
