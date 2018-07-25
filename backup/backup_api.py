from .backups import *

def init_black_box():
    backup_manage().init_backups()
    backup_manage().register_blackbox_step_notify(blackbox_step_notify)

# 获取日志类型
def get_agv_types(robot_list):
    return backup_manage().get_agv_types(robot_list)

#下发获取日志的筛选条件
def send_log_condition(robot_list, user_id, start_time, end_time, types, name):
    return backup_manage().send_log_condition(robot_list, user_id, start_time, end_time, types, name)

# 取消任务
def cancel_get_log(task_id):
    return backup_manage().cancel_get_log(task_id)

# 正在执行的任务
def get_executing_log(user_id):
    return backup_manage().get_executing_log(user_id)

# 删除日志文件
def delete_log(user_id, log_name):
    return backup_manage().delete_log(user_id, log_name)

# 用户下的日志文件
def get_log_list(user_id):
    return backup_manage().get_log_list(user_id)

# 获取后台要下载文件的全路径
def download_log(user_id, log_name):
    return backup_manage().download_log(user_id, log_name)

def blackbox_step_notify(dict):
    if notify_step_function is not None:
            notify_step_function(dict)

def register_blackbox_step_notify(log_notify=None):
    global notify_step_function
    notify_step_function = log_notify

