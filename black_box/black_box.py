from agvshell.shell_api import pull_file_from_remote,register_notify_log_step,cancle_file_transform
from pynsp.waite_handler import *
from pynsp.logger import *
from agvshell.shproto import proto_log as log
from agvshell.file_rw import *
from agvshell.shell_manager import shell_manager
import errtypes
import os, sys
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

    # for id in robot_list:
    #     shell_info = shell_manager().get_session_by_id(int(robot_list))
    #     if shell_info is not None:
    #         pkt_id = shell_info.load_log_type()
    #         if pkt_id < 0:
    #             Logger().get_logger().error("failed post get log type to agvshell.")
    #             break
    #         # 同步等待
    #         if wait_handler().wait_simulate(pkt_id, 3000) >= 0:
    #             data = shell_info.get_log_types()
    #             type_list = log.proto_log_type_vct()
    #             type_list.build(data, 0)
    #             for index in type_list.log_type_vct:
    #                 log_type[index.log_type.value]=0#取并集
    #                 print('log_type:', index.log_type.value)
    #             wait_handler().wait_destory(pkt_id)
    shell_info = shell_manager().get_session_by_id(int(robot_list))
    if shell_info is not None:
        pkt_id=shell_info.load_log_type()
        if pkt_id < 0:
            Logger().get_logger().error("failed post get log type to agvshell.")
            # break
        # 同步等待
        if wait_handler().wait_simulate(pkt_id, 3000) >= 0:
            data = shell_info.get_log_types()
            type_list = log.proto_log_type_vct()
            type_list.build(data, 0)
            print('type length:', len(type_list.log_type_vct))
            type_list=[]
            for index in type_list.log_type_vct:
                type_list.append(index.log_type.value)
                print('log_type:', index.log_type.value)
            wait_handler().wait_destory(pkt_id)
            return type_list


#对外接口：下发获取日志的筛选条件
def send_log_condition(robot_list,user_id,start_time,end_time,types,name):
    task_id=get_task_id()
    global task_user_,user_task_data,task_id_count_,task_recv_count_
    task_user_[task_id]=user_id
    print('task-user',task_user_[task_id])
    task_id_count_[user_id]=0
    task_recv_count_[user_id]=0
    zip_file=get_user_path(user_id)+name
    hzip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    mutex.acquire()
    user_task_data[user_id]={'task':task_id,'name':zip_file,'handle':hzip,'path':{}}
    mutex.release()
    robot_list = {2}
    for id in robot_list:
        shell_info = shell_manager().get_session_by_id(int(id))
        if shell_info is not None:
            if shell_info.get_log_data(task_id, start_time, end_time, types)>=0:
                shell_info.register_notify_log_path(load_log_path)
                task_id_count_[user_id] +=1#发送成功的个数

#取消任务
def cancle_get_log(task_id):
    user=task_user_[task_id]
    mutex.acquire()
    if user_task_data[user] is not None:
        for id in user_task_data[user][task_id]:
            shell_info = shell_manager().get_session_by_id(int(id))
            if shell_info is not None:
                ret=shell_info.cancle_log_data()
                list=cancle_file_transform(user, id, task_id)
                if len(list)>0 and ret>=0:
                    return 0
        mutex.release()
    return -1


#收到车上shell压缩的文件，返回的车上路径
def load_log_path(id,task_id,data):
    global task_user_
    print('back----',task_id)
    path = log.proto_logs_file_path()
    path.build(data, 0)
    print('build',task_id,len(path.vct_log_file_name))
    user=task_user_[int(task_id)]
    mutex.acquire()
    if len(path.vct_log_file_name)!=0 and user_task_data[user]['path'] is not None:
        print('id_log_path', id, path.vct_log_file_name[0])
        user_task_data[user]['path'][id] = path.vct_log_file_name[0].value
        #log_path[id]=path.vct_log_file_name[0]
        # fts去取压缩好的文件
        strpath=path.vct_log_file_name[0].value
        local_path=get_user_path(user)+str(id)+'_'+strpath[strpath.rfind('/') + 1:]
        print('local_path--',local_path)
        route_path_list=[{'robot_id':id,'file_path':path.vct_log_file_name[0].value,'local_path':local_path}]
        pull_file_from_remote(user,  FILE_TYPE_BLACKBOX_PULL_FILES, route_path_list)
    mutex.release()

#压缩文件
def zip_threading_func(file_path,user_id):
    mutex.acquire()
    open_path = get_user_path(user_id)
    print('write------',file_path,open_path)
    #os.chdir(open_path)  # 转到路径
    global user_task_data
    filefullpath = os.path.join(open_path, file_path)
    user_task_data[user_id]['handle'].write(filefullpath,file_path)
    user_task_data[user_id]['handle'].write(filefullpath,'2_log_20180709_100251.tar.xz')
    user_task_data[user_id]['handle'].write(filefullpath, '2_log_20180709_100310.tar.xz')
    user_task_data[user_id]['handle'].close()
    mutex.release()

#pull文件时，回调进度
def pull_log_step_notify(user_id,robot_id,step,file_path,error_code):#file_path需要改成保存后台的文件名,status状态表示file_rw推拉是否正常
    print('step',step)
    notify_dic = dict()
    notify_dic['msg_type'] = errtypes.TypeShell_Blackbox_Log
    notify_dic['user_id'] = user_id
    global task_id_count_,task_recv_count_
    mutex.acquire()
    if step==100 :
        task_recv_count_[int(user_id)]+=1
        tmp=str(robot_id) + '_' + file_path[file_path.rfind('/') + 1:]#get_user_path(user_id) + str(robot_id) + '_' + file_path[file_path.rfind('/') + 1:]
        t = threading.Thread(target=zip_threading_func, args=(tmp,int(user_id)))
        #t.setDaemon(True)
        t.start()
    if error_code < 0:
        task_recv_count_[int(user_id)] += 1

    print('type',task_recv_count_,task_id_count_)
    if task_recv_count_[int(user_id)]==task_id_count_[int(user_id)]:
        notify_dic['step'] = 100
        #推送前台
        pass  # 压缩完删除文件
    else:
        sch = (task_recv_count_[int(user_id)]+float(step) / 100) / task_id_count_[int(user_id)]  # 总进度
        notify_dic['step']=sch
        # sockio推给前台
    mutex.release()

#获取存后台的路径
def get_user_path(user_id):
    user_name = user.query_name_by_id(user_id)
    folder_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER

    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)

    return folder_path

    #file_path = os.path.join(folder_path, filename)


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