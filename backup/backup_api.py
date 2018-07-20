from .backups import *

def init_black_box():
    backup_manage().init_backups()
    backup_manage().register_blackbox_step_notify(blackbox_step_notify)

def get_agv_types(robot_list):
    return backup_manage().get_agv_types(robot_list)

def send_log_condition(robot_list, user_id, start_time, end_time, types, name):
    return backup_manage().send_log_condition(robot_list, user_id, start_time, end_time, types, name)

def cancle_get_log(task_id):
    return backup_manage().cancle_get_log(task_id)

def get_executing_log(user_id):
    return backup_manage().get_executing_log(user_id)

def delete_log(user_id, log_name):
    return backup_manage().delete_log(user_id, log_name)

def get_log_list(user_id):
    return backup_manage().get_log_list(user_id)

def download_log(user_id, log_name):
    return backup_manage().download_log(user_id, log_name)

def blackbox_step_notify(dict):
    if notify_step_function is not None:
            notify_step_function(dict)

def register_blackbox_step_notify(log_notify=None):
    global notify_step_function
    notify_step_function = log_notify

