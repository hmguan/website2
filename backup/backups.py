from agvshell.shell_api import pull_file_from_remote,register_notify_log_step,cancle_file_transform
from pynsp.waite_handler import *
from pynsp.logger import *
from agvshell.shproto import proto_log as log
from agvshell.file_rw import *
from agvshell.shell_manager import shell_manager
import errtypes
import os, sys,tarfile,shutil
import zipfile
from db.db_users import user
from configuration import config

notify_step_function=None
thread_wait = waitable_handle(True)
@slt.singleton
class backup_manage():
    def __init__(self):
        self.user_task_data=dict()
        self.task_id_count_=dict()
        self.task_recv_count_=dict()
        self.task_user_=dict()
        self.task_id_=0
        self.tar_list=[]
        self.mutex = threading.RLock()
        self.__check_timeout = threading.Thread(target=backup_manage.tar_threading_func, args=(self,))
        self.__check_timeout.setDaemon(True)
        self.__check_timeout.start()
        pass

    def __del__(self):
        self.__is_exist_th = True
        self.__check_timeout.join()
        print('mt_manage __del__')

    # 初始化注册进度回调
    def init_backups(self):
        print('init black')
        register_notify_log_step(self.pull_log_step_notify)

    # 全局任务id
    def get_task_id(self) -> int:
        self.task_id_ = self.task_id_ + 1
        return self.task_id_

    # 获取日志类型
    def get_agv_types(self,robot_list):
        log_type = dict()
        ret_list = []
        for id in robot_list:
            shell_info = shell_manager().get_session_by_id(int(id))
            if shell_info is not None:
                pkt_id = shell_info.load_log_type()
                if pkt_id < 0:
                    Logger().get_logger().error("failed post get log type to agvshell.")
                    continue
                # 同步等待
                if wait_handler().wait_simulate(pkt_id, 3000) >= 0:
                    data = shell_info.get_log_types()
                    type_list = log.proto_log_type_vct()
                    try:
                        type_list.build(data, 0)
                    except:
                        pass
                    for index in type_list.log_type_vct:
                        log_type[index.log_type.value] = 0  # 取并集
                        print('log_type:', index.log_type.value)
                    wait_handler().wait_destory(pkt_id)
        for index in log_type.keys():
            ret_list.append(index)
        return ret_list

    # 下发获取日志的筛选条件
    def send_log_condition(self,robot_list, user_id, start_time, end_time, types, name):
        task_id = self.get_task_id()
        lists=list()
        self.task_user_[task_id] = user_id
        print('task-user', self.task_user_[task_id])
        self.task_id_count_[int(user_id)] = 0
        self.task_recv_count_[int(user_id)] = 0
        zip_file = self.get_user_path(user_id) + name
        self.get_user_tmp_path(user_id)
        hzip = tarfile.open(zip_file, "w:tar")
        # hzip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        self.mutex.acquire()
        self.user_task_data[user_id] = {'task': task_id, 'filepath': zip_file, 'name': name, 'handle': hzip, 'path': {},
                                   'step': 0, 'pull_list':lists}
        self.mutex.release()
        for id in robot_list:
            shell_info = shell_manager().get_session_by_id(int(id))
            if shell_info is not None:
                if shell_info.get_log_data(task_id, start_time, end_time, types) >= 0:
                    shell_info.register_notify_log_path(self.load_log_path)
                    self.task_id_count_[user_id] += 1  # 发送成功的个数
                    self.user_task_data[user_id]['path'][id] = ''

        if self.task_id_count_[user_id] == 0:
            self.user_task_data[user_id]['handle'].close()
            self.delete_log(user, self.user_task_data[user]['name'])
            self.delete_tmp_file(user)
            del self.task_user_[task_id]
            del self.user_task_data[user]
            return -1
        return task_id

    # 取消任务
    def cancel_get_log(self,task_id):
        if not self.task_user_.__contains__(task_id):
            return -1
        user = self.task_user_[task_id]
        if self.user_task_data.__contains__(user):
            for id in self.user_task_data[user]['path'].keys():
                shell_info = shell_manager().get_session_by_id(int(id))
                if shell_info is not None:
                    shell_info.cancle_log_data(task_id)
                    cancle_file_transform(user, id, self.user_task_data[user]['pull_list'])
            self.user_task_data[user]['handle'].close()
            self.delete_tmp_file(user)
            self.delete_log(user,self.user_task_data[user]['name'])
            del self.user_task_data[user]
            del self.task_user_[task_id]
            Logger().get_logger().info('cancel get log task:{0}'.format(task_id))
            return 0
        return -1

    # 正在执行的任务
    def get_executing_log(self,user_id):
        if self.user_task_data.__contains__(user_id):
            return self.user_task_data[user_id]['name'], self.user_task_data[user_id]['task'], self.user_task_data[user_id]['step']

        return '', -1, -1

    # 删除日志文件
    def delete_log(self,user_id, log_name):
        path = self.get_user_path(user_id)
        if os.path.isfile(path + log_name):
            os.remove(path + log_name)
            return 0
        return -1

    #删除零时文件夹
    def delete_tmp_file(self,user):
        file = self.get_user_tmp_path(user)
        if os.path.exists(file):
            shutil.rmtree(file)
            return 0
        return -1

    # 用户下的日志文件
    def get_log_list(self,user_id):
        file_list = []
        path = self.get_user_path(user_id)
        list = os.listdir(path)
        for index in list:
            attr = dict()
            print('path', index)
            if os.path.isfile(path + index) and os.path.splitext(index)[1] == ".tar":
                #pastTime = (datetime.datetime.now() - datetime.timedelta(days=15)).strftime('%Y/%m/%d %H:%M:%S')
                timestamp = os.path.getmtime(path + index)
                filetime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(timestamp))
                #size = os.path.getsize(path + index)
                #if filetime < pastTime or size == 0:  # 删除超过15天的
                    #os.remove(path + index)
                #else:
                attr['time'] = filetime
                attr['path'] = index
                attr['size'] = os.path.getsize(path + index)
                file_list.append(attr)
        return file_list

    # 收到车上shell压缩的文件，返回的车上路径
    def load_log_path(self,id, stat, data):
        print('back----', stat,id,data,self.user_task_data)
        global notify_step_function
        if stat == -1 and data == '':  # shell此时断连的话
            for user in self.user_task_data.keys():
                if self.user_task_data[user]['path'].__contains__(id) and self.user_task_data[user]['path'][id]=='':#==''表示车上没有压完文件，就断开了
                    if self.task_user_.__contains__(self.user_task_data[user]['task']):
                        if self.user_task_data[user]['path'][id] == 'null':
                            return
                        self.task_id_count_[user] -= 1
                        if self.failed_get_log(user)<0:
                            return
                else:
                    return

        Logger().get_logger().info('shell back')
        path = log.proto_logs_file_path()
        path.build(data, 0)
        if not self.task_user_.__contains__(int(path.task_id)):
            return
        user = self.task_user_[int(path.task_id)]
        if len(path.vct_log_file_name) == 0:  # 没有文件返回
            Logger().get_logger().warning('not find any log files :by user {0} robot id:{1}'.format(user, id))
            self.user_task_data[user]['path'][id] = 'null'
            if self.task_user_.__contains__(self.user_task_data[user]['task']):
                self.task_id_count_[user] -= 1
                if self.failed_get_log(user) < 0:
                    return
        self.mutex.acquire()
        if len(path.vct_log_file_name) != 0 and path.task_id==self.user_task_data[user]['task']:
            print('id_log_path', id, path.vct_log_file_name[0])
            # fts去取压缩好的文件
            strpath = path.vct_log_file_name[0].value
            local_path = self.get_user_tmp_path(user) + str(id) + '_' + strpath[strpath.rfind('/') + 1:]
            self.user_task_data[user]['path'][id] = local_path
            print('local_tmp_path', local_path)
            route_path_list = [{'robot_id': id, 'file_path': path.vct_log_file_name[0].value, 'local_path': local_path}]
            task,err = pull_file_from_remote(user, FILE_TYPE_BLACKBOX_PULL_FILES, route_path_list)
            if len(task) > 0:
                self.user_task_data[user]['pull_list'].append(task[0])
        self.mutex.release()

    # 压缩文件
    def tar_threading_func(self):
        global notify_step_function,thread_wait
        while True:
            if thread_wait.wait(0xffffffff) == False:
                pass
            if len(self.tar_list) > 0:
                user_id = self.tar_list[0]['user']
                file_path = self.tar_list[0]['path']
                if self.user_task_data[int(user_id)]['handle'] is not None:
                    handle = self.user_task_data[user_id]['handle']
                open_path = self.get_user_tmp_path(user_id)
                print('write------', file_path, open_path, self.tar_list)
                Logger().get_logger().info('tar log')
                filefullpath = os.path.join(open_path, file_path)
                if os.path.isfile(filefullpath):
                    handle.add(filefullpath, arcname=file_path)
                del self.tar_list[0]
                # handle.write(filefullpath,file_path)
                if self.user_task_data[int(user_id)]['step'] == 100 :
                    handle.close()
                    print('close task')
                    if os.path.exists(open_path):
                        shutil.rmtree(open_path)
                    if notify_step_function is not None:
                        notify_step_function({'step': 100, 'msg_type': errtypes.TypeShell_Blackbox_Log, 'user_id': user_id,
                                          'task_id': self.user_task_data[user_id]['task']})
                Logger().get_logger().info('tar log over')

    # pull文件时，回调进度
    def pull_log_step_notify(self,user_id, robot_id, step, file_path, error_code,status):  # file_path需要改成保存后台的文件名,status状态表示file_rw推拉是否正常
        global notify_step_function ,thread_wait
        if file_path=='':
            #最后一个断线or没有文件，
            self.user_task_data[int(user_id)]['step'] = 100
            notify_step_function({'step': 100, 'msg_type': errtypes.TypeShell_Blackbox_Log, 'user_id': user_id,
                                  'task_id': self.user_task_data[user_id]['task']})
        print('step', step, error_code, status)

        if step == 100 and status == 1:
            self.task_recv_count_[int(user_id)] += 1
            tmp = str(robot_id) + '_' + file_path[file_path.rfind(
                '/') + 1:]  # get_user_path(user_id) + str(robot_id) + '_' + file_path[file_path.rfind('/') + 1:]
            if self.task_recv_count_[int(user_id)] == self.task_id_count_[int(user_id)]:
                self.user_task_data[int(user_id)]['step'] = 100
            self.tar_list.append({'path': tmp, 'user': int(user_id)})
            thread_wait.sig()
        if error_code != 0:
            self.user_task_data[user_id]['path'][id] = 'null'
            self.task_recv_count_[int(user_id)] += 1
            if self.task_recv_count_[int(user_id)] == self.task_id_count_[int(user_id)]:
                if self.task_recv_count_[int(user_id)] != 0:
                    notify_step_function({'step': 100, 'msg_type': errtypes.TypeShell_Blackbox_Log, 'user_id': user_id,
                                          'task_id': self.user_task_data[user_id]['task']})

        self.mutex.acquire()
        if self.task_recv_count_[int(user_id)] == self.task_id_count_[int(user_id)]:
            pass
        else:
            if step == 100 and status == 1:
                sch = 100 * self.task_recv_count_[int(user_id)] // self.task_id_count_[int(user_id)]  # 总进度
            else:
                sch = (100 * self.task_recv_count_[int(user_id)] + step) // self.task_id_count_[int(user_id)]  # 总进度
            self.user_task_data[int(user_id)]['step'] = sch
            if notify_step_function is not None:
                notify_step_function({'step': sch, 'msg_type': errtypes.TypeShell_Blackbox_Log, 'user_id': user_id,
                                          'task_id': self.user_task_data[user_id]['task']})
        self.mutex.release()

    def register_blackbox_step_notify(self,log_notify=None):
        global notify_step_function
        notify_step_function = log_notify

    #获取失败or断连
    def failed_get_log(self,user):
        global notify_step_function
        self.mutex.acquire()
        if self.task_id_count_[user] == 0:
            if notify_step_function is not None:
                notify_step_function({'msg_type': errtypes.TypeShell_Blackbox_None, 'user_id': user,'task_id':self.user_task_data[user]['task']})
            self.user_task_data[user]['handle'].close()
            self.delete_log(user, self.user_task_data[user]['name'])
            self.delete_tmp_file(user)
            del self.task_user_[self.user_task_data[user]['task']]
            del self.user_task_data[user]
            self.mutex.release()
            return -1
        elif self.task_id_count_[user] == self.task_recv_count_[user]:
            self.pull_log_step_notify(user, id, 100, '', 0, 1)  # 最后一个断线
            self.mutex.release()
            return 0
        self.mutex.release()


    # 获取存后台的路径
    def get_user_path(self,user_id):
        user_name = user.query_name_by_id(user_id)
        folder_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER
        if os.path.exists(folder_path) == False:
            os.makedirs(folder_path)
        return folder_path

    def get_user_tmp_path(self,user_id):
        user_name = user.query_name_by_id(user_id)
        tmp_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER + 'tmp/'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        return tmp_path

    # 获取后台要下载文件的全路径
    def download_log(self,user_id, log_name):
        path = self.get_user_path(user_id)
        list = os.listdir(path)
        for index in list:
            if os.path.isfile(path + index) and os.path.splitext(index)[1] == ".tar" and os.path.join(
                    path + log_name) == os.path.join(path + index):
                filepath = os.path.join(path + log_name)
                return filepath[1:len(filepath)]
        return ''



# #task_data_=dict()
# user_task_data=dict()
# #{user1:{task:1,name:1.zip,log_path:{id1:1.log,id2:2.log,id3:3.log}}
# # user2:{task:2,name:2.zip,log_path:{id1:1.log,id2:2.log,id3:3.log}}}
# task_id_count_=dict()#一个任务总robot数
# task_recv_count_=dict()#一个任务回的robot数
# #task_id--user_id
# task_user_=dict()
# task_id_=0
# mutex = threading.RLock()
# notify_step_function=None
# tar_list=[]












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