from .backup_api import *

def start_black_box():
    init_black_box()

def register_blackbox_step_notify_function(notify_call=None):
    '''
    regist notification of browser,while pull logs,
    it will push step to browser via socketio
    :param notify_call:
    :return:
    '''
    from .backup_api import register_blackbox_step_notify
    register_blackbox_step_notify(notify_call)