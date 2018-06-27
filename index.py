from app import create_app,create_socketio
from agvinfo.dhcp_agent_center import start_agvinfo_service
from agvshell import start_agvshell_manager,register_notify_function
from agvmt import start_mt_manager,register_mt_notify_function
from pynsp.logger import *
import traceback
import sys
#import ptvsd

ptvsd.settrace(None, ('0.0.0.0', 12345))

app=create_app('default')
local_socketio = create_socketio(app)

# 异常处理函数
def quiet_errors(exc_type, exc_value, tb):
    Logger().get_logger().error(''.join(traceback.format_exception(exc_type, exc_value, tb)))

# 定义全局异常捕获
sys.excepthook = quiet_errors

if __name__ == '__main__':
    from app.soketio import sockio_api as soket_center

    #初始化日志文件
    init_logger()
    #启动agvinfo server服务
    start_agvinfo_service()
    #启动agvshell manager管理服务
    start_agvshell_manager()
    #启动mt_manage管理服务
    start_mt_manager()
    #注册通知浏览器mt错误回调
    register_mt_notify_function(notify_call=soket_center.response_to_client_data)
    #注册通知浏览器回调例程
    register_notify_function(notify_call = soket_center.response_to_client_data)
    #启动socket io服务
    local_socketio.run(app,host='0.0.0.0', port=5008, debug=True,use_reloader=False)
