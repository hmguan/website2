from agvshell.shell_api import pull_file_from_remote,register_notify_log_step,cancle_file_transform
from pynsp.waite_handler import *
from pynsp.logger import *
from agvshell.shproto import proto_log as log
from agvshell.file_rw import *
from agvshell.shell_manager import shell_manager
import errtypes
import os, sys,tarfile
import zipfile
from db.db_users import user
from configuration import config

#task_data_=dict()
user_task_data=dict()
#{user1:{task:1,name:1.zip,log_path:{id1:1.log,id2:2.log,id3:3.log}}
# user2:{task:2,name:2.zip,log_path:{id1:1.log,id2:2.log,id3:3.log}}}
task_id_count_=dict()#一个任务总robot数
task_recv_count_=dict()#一个任务回的robot数
#task_id--user_id
task_user_=dict()
task_id_=0
mutex = threading.RLock()
notify_step_function=None
#初始化注册进度回调
def init_black_box():
    print('init black')
    register_notify_log_step(pull_log_step_notify)

#全局任务id
def get_task_id()->int:
    global task_id_
    task_id_=task_id_+1
    return task_id_

#对外接口：获取日志类型
def get_agv_types(robot_list):
    log_type=dict()
    ret_list=[]
    for id in robot_list:
        shell_info = shell_manager().get_session_by_id(int(id))
        if shell_info is not None:
            pkt_id = shell_info.load_log_type()
            if pkt_id < 0:
                Logger().get_logger().error("failed post get log type to agvshell.")
                break
            # 同步等待
            if wait_handler().wait_simulate(pkt_id, 3000) >= 0:
                data = shell_info.get_log_types()
                type_list = log.proto_log_type_vct()
                type_list.build(data, 0)
                for index in type_list.log_type_vct:
                    log_type[index.log_type.value]=0#取并集
                    print('log_type:', index.log_type.value)
                wait_handler().wait_destory(pkt_id)
    for index in log_type.keys():
        ret_list.append(index)
        print('log_type:', index)
    return ret_list


#对外接口：下发获取日志的筛选条件
def send_log_condition(robot_list,user_id,start_time,end_time,types,name):
    task_id=get_task_id()
    global task_user_,user_task_data,task_id_count_,task_recv_count_
    task_user_[task_id]=user_id
    print('task-user',task_user_[task_id])
    task_id_count_[int(user_id)]=0
    task_recv_count_[int(user_id)]=0
    zip_file=get_user_path(user_id)+name
    hzip = tarfile.open(zip_file, "w:tar")
    # hzip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    mutex.acquire()
    user_task_data[user_id]={'task':task_id,'filepath':zip_file,'name':name,'handle':hzip,'path':{},'step':0}
    mutex.release()
    # robot_list={2,3}
    for id in robot_list:
        shell_info = shell_manager().get_session_by_id(int(id))
        if shell_info is not None:
            if shell_info.get_log_data(task_id, start_time, end_time, types)>=0:
                shell_info.register_notify_log_path(load_log_path)
                task_id_count_[user_id] +=1#发送成功的个数
            # else: return -1
    if task_id_count_[user_id]==0:
        user_task_data[user_id]['handle'].close()
        return -1
    return 0

#取消任务
def cancle_get_log(task_id):
    user=task_user_[task_id]
    if user_task_data.__contains__(user) is not None:
         for id in user_task_data[user]['path'].keys():
            shell_info = shell_manager().get_session_by_id(int(id))
            if shell_info is not None:
                ret=shell_info.cancle_log_data()
                cancle_file_transform(user, id, task_id)
                if ret>=0:
                    del user_task_data[user]
                    return 0
    return -1

#正在执行的任务
def get_executing_log(user_id):

    global user_task_data
    if user_task_data.__contains__(user_id):
        return user_task_data[user_id]['name'],user_task_data[user_id]['task'],user_task_data[user_id]['step']

    return '',-1, -1

#删除日志文件
def delete_log(user_id,log_name):
    path=get_user_path(user_id)
    if os.path.isfile(path + log_name):
        os.remove(path + log_name)
        return 0
    return -1

#用户下的日志文件
def get_log_list(user_id):
    global user_task_data
    file_list=[]
    path = get_user_path(user_id)
    list=os.listdir(path)
    for index in list:
        attr=dict()
        print('path',index)
        if os.path.isfile(path+index) and os.path.splitext(index)[1] == ".tar":
            attr['path']=index
            timestamp=os.path.getmtime(path+index)
            attr['time'] =time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(timestamp))
            attr['size']=os.path.getsize(path+index)
            file_list.append(attr)
    return file_list


#收到车上shell压缩的文件，返回的车上路径
def load_log_path(id,task_id,data):
    global task_user_,notify_step_function
    print('back----',task_id)
    Logger().get_logger().info('shell back')
    path = log.proto_logs_file_path()
    path.build(data, 0)
    user = task_user_[int(task_id)]
    print('user',user,len(path.vct_log_file_name),user_task_data[user]['path'])
    if len(path.vct_log_file_name)==0:#没有文件返回
        if notify_step_function is not None:
            notify_step_function({'msg_type':errtypes.TypeShell_Blackbox_None,'user_id':user})
    mutex.acquire()
    if len(path.vct_log_file_name)!=0:# and user_task_data[user]['path'] is not None:
        print('id_log_path', id, path.vct_log_file_name[0])
        #del user_task_data[user]
        # fts去取压缩好的文件
        strpath=path.vct_log_file_name[0].value
        local_path=get_user_path(user)+str(id)+'_'+strpath[strpath.rfind('/') + 1:]
        user_task_data[user]['path'][id]=local_path
        print('local_path--',local_path)
        route_path_list=[{'robot_id':id,'file_path':path.vct_log_file_name[0].value,'local_path':local_path}]
        pull_file_from_remote(user,  FILE_TYPE_BLACKBOX_PULL_FILES, route_path_list)
    mutex.release()

#压缩文件
def zip_threading_func(file_path,user_id):
    mutex.acquire()
    global user_task_data,notify_step_function
    if user_task_data[int(user_id)]['handle'] is not None:
        handle=user_task_data[user_id]['handle']
    mutex.release()
    open_path = get_user_path(user_id)
    print('write------',file_path,open_path)
    Logger().get_logger().info('tar log')
    filefullpath = os.path.join(open_path, file_path)
    handle.add(filefullpath,arcname=file_path)
    # handle.write(filefullpath,file_path)
    if user_task_data[int(user_id)]['step']==100 and notify_step_function is not None:
        handle.close()
        print('close task')
        notify_step_function({'step':100,'msg_type':errtypes.TypeShell_Blackbox_Log,'user_id':user_id,'task_id':user_task_data[user_id]['task']})
    # os.remove(filefullpath)
    Logger().get_logger().info('tar log over')

#pull文件时，回调进度
def pull_log_step_notify(user_id,robot_id,step,file_path,error_code,status):#file_path需要改成保存后台的文件名,status状态表示file_rw推拉是否正常
    print('step',step,error_code,status)
    notify_dic = dict()
    notify_dic['msg_type'] = errtypes.TypeShell_Blackbox_Log
    notify_dic['user_id'] = user_id
    global task_id_count_,task_recv_count_,user_task_data,notify_step_function

    if step==100 and status==1:
        task_recv_count_[int(user_id)]+=1
        tmp=str(robot_id) + '_' + file_path[file_path.rfind('/') + 1:]#get_user_path(user_id) + str(robot_id) + '_' + file_path[file_path.rfind('/') + 1:]
        if task_recv_count_[int(user_id)]==task_id_count_[int(user_id)]:
            user_task_data[int(user_id)]['step'] = 100
        t = threading.Thread(target=zip_threading_func, args=(tmp,int(user_id)))
        #t.setDaemon(True)
        t.start()
    if error_code != 0:
        task_recv_count_[int(user_id)] += 1
    mutex.acquire()
    if task_recv_count_[int(user_id)]==task_id_count_[int(user_id)]:
        # user_task_data[user_id]['step'] =100
        # notify_dic['step'] = 100
        # notify_dic['task_id'] =user_task_data[user_id]['task']
        # if notify_step_function is not None:
        #     notify_step_function(notify_dic)
        pass
    else:
        if step==100 and status==1:
            sch = 100*task_recv_count_[int(user_id)] // task_id_count_[int(user_id)]  # 总进度
        else:
            sch = (100*task_recv_count_[int(user_id)]+step) // task_id_count_[int(user_id)] # 总进度
        print('data',user_task_data)
        user_task_data[int(user_id)]['step'] =sch
        notify_dic['step']=sch
        notify_dic['task_id'] = user_task_data[user_id]['task']
        if notify_step_function is not None:
            notify_step_function(notify_dic)
    mutex.release()

def register_blackbox_step_notify(log_notify=None):
    global notify_step_function
    notify_step_function = log_notify

#获取存后台的路径
def get_user_path(user_id):
    user_name = user.query_name_by_id(user_id)
    folder_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER

    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)

    return folder_path


# from flask import request, jsonify, send_from_directory, abort
# import os

#后台的文件下到用户电脑上
def download_log(user_id,log_name):
    path = get_user_path(user_id)
    list = os.listdir(path)
    for index in list:
        if os.path.isfile(path + index) and os.path.splitext(index)[1] == ".tar" and os.path.join(path + log_name)==os.path.join(path + index):
            filepath=os.path.join(path + log_name)
            return filepath[1:len(filepath)]
    return ''

    # pass
    # path=get_user_path(user_id)
    # if os.path.isfile(os.path.join(path, log_name)):
    #     print('----is')
    #     return send_from_directory(path, log_name, as_attachment=True)

if __name__ == "__main__":

    open_path = '/root/zip_test_data/'
    os.chdir(open_path)  # 转到路径
    files = ['1.txt', '2.txt','3.txt']  # 文件的位置，多个文件用“，”隔开
    zip_file = '/root/zip_test_data/11asdf.zip'  # 压缩包名字
    #os.chdir(open_path)
    zip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    for file in files:
        print('compressing', file)
        zip.write(file)
    zip.close()
    print('compressing finished')