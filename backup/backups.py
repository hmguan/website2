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
from copy import deepcopy
from time import sleep
from db.db_file_list import *

BlackboxFailed=-1
BlackboxTarFailed=-5
BlackboxShellCancel=-105
BlackboxDisconnect=-102
BlackboxPullFailed=-103
BlackboxInsertSqlFaild=-104
BlackboxSearchSqlFailed=-106
BlackboxNoLog=-107

notify_step_function=None
thread_wait = waitable_handle(True)
@slt.singleton
class backup_manage():
    def __init__(self):
        self.user_task_data=dict()
        self.task_user_=dict()
        self.task_id_=0
        self.mutex = threading.RLock()
        self.task_mutex=threading.RLock()
        self.__userid_to_name=dict()
        pass

    def __del__(self):
        self.__is_exist_th = True
        # self.__check_timeout.join()
        print('mt_manage __del__')

    # 初始化注册进度回调
    def init_backups(self):
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
                    wait_handler().wait_destory(pkt_id)
                    type_list = shell_info.get_log_types()
                    for index in type_list.log_type_vct:
                        log_type[index.log_type.value] = 0  # 取并集
                        print('log_type:', index.log_type.value)
                else:
                    Logger().get_logger().error('failed get log type,robot:{0} it is timeout'.format(id))
        for index in log_type.keys():
            ret_list.append(index)
        return ret_list

    # 下发获取日志的筛选条件
    def send_log_condition(self,robot_list, user_id, start_time, end_time, types, name):
        (ret,user_name) =user.query_name_by_id(user_id)
        if -1==ret:
            return -3
        if -2==ret:
            return -4
        
        self.__userid_to_name[user_id]=user_name
        self.mutex.acquire()
        print('mutes-send-acquire-0')
        if self.user_task_data.__contains__(user_id):
            if self.user_task_data[user_id]['step']!=100:#
                self.mutex.release()
                return -2
            if self.user_task_data[user_id]['tar']==0 and self.user_task_data[user_id]['step']==100:
                self.mutex.release()
                return -2
        task_id = self.get_task_id()
        self.task_user_[task_id] = user_id
        zip_file = self.get_user_path(user_id) + name
        zip_file_tmp=self.get_user_tmp_path(user_id)+name
        hzip = tarfile.open(zip_file_tmp, "w:tar")

        self.user_task_data[user_id] = {'task': task_id, 'filepath': zip_file, 'name': name, 'handle': hzip, 'path': {},
                                   'step': 0, 'pull_list':[],'failed':[],'success':[],'wait':[],'shellback':[],'status':0,'tar':1,'delete':0,'err':0}
        # self.mutex.release()
        for id in robot_list:
            shell_info = shell_manager().get_session_by_id(int(id))
            if shell_info is not None:
                shell_info.register_notify_log_path(self.load_log_path)
                if shell_info.get_log_data(task_id, start_time, end_time, types) >= 0:
                    self.user_task_data[user_id]['wait'].append(int(id))
                    self.user_task_data[user_id]['path'][int(id)] = ''
        if len(self.user_task_data[user_id]['wait'])==0:
            self.user_task_data[user_id]['handle'].close()
            self.delete_log(user_id, self.user_task_data[user_id]['name'])
            self.delete_tmp_file(user_id)
            del self.task_user_[task_id]
            del self.user_task_data[user_id]
            print('mutes-send-release-0')
            self.mutex.release()
            return -1
        print('mutes-send-release-0')
        self.mutex.release()
        return task_id

    # 取消任务
    def cancel_get_log(self,task_id):
        ret=-1
        if not self.task_user_.__contains__(task_id):
            return ret
        user_id=deepcopy(self.task_user_[task_id])
        self.mutex.acquire()
        if self.user_task_data.__contains__(user_id):
            ret = 0
            # self.mutex.acquire()
            self.user_task_data[user_id]['status']=1
            for id in self.user_task_data[user_id]['path'].keys():
                print('curr_task',self.user_task_data[user_id])
                shell_info = shell_manager().get_session_by_id(int(id))
                if shell_info is not None:
                    Logger().get_logger().info('cancel pull task:{0}'.format(self.user_task_data[user_id]['pull_list']))
                    if not self.user_task_data[user_id]['shellback'].__contains__(id):
                        shell_info.cancle_log_data(task_id)
            remove_list=cancle_file_transform(user_id, self.user_task_data[user_id]['pull_list'])
            if self.user_task_data[user_id]['tar']==0:#正在压缩
                self.user_task_data[user_id]['delete'] = 1
                ret = 1  # 等待压缩
            else:
                self.user_task_data[user_id]['handle'].close()
                self.delete_tmp_file(user_id)
                self.delete_log(user_id,self.user_task_data[user_id]['name'])
                del self.user_task_data[user_id]
                del self.task_user_[task_id]

            self.mutex.release()

            Logger().get_logger().info('cancel get log task:{0}'.format(task_id))
            return ret
        self.mutex.release()
        return ret

    # 正在执行的任务
    def get_executing_log(self,user_id):
        if self.user_task_data.__contains__(user_id):
            return self.user_task_data[user_id]['name'], self.user_task_data[user_id]['task'], self.user_task_data[user_id]['step']
        return '', -1, -1

    # 删除日志文件
    def delete_log(self,user_id, log_name):
        path = self.get_user_path(user_id)
        if os.path.isfile(path + log_name):
            try:
                os.remove(path + log_name)
            except:
                return -1
            return 0
        return -1

    #删除零时文件夹
    def delete_tmp_file(self,user_id):
        file = self.get_user_tmp_path(user_id)
        if os.path.exists(file):
            try:
                shutil.rmtree(file)
            except:
                return -1
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
                timestamp = os.path.getmtime(path + index)
                filetime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(timestamp))
                attr['time'] = filetime
                attr['path'] = index
                attr['size'] = os.path.getsize(path + index)
                file_list.append(attr)
        return file_list

    def is_disconnect(self,id):
        print('mutes-dis-acquire-0')
        self.mutex.acquire()
        for user_id in self.user_task_data.keys():
            if self.user_task_data[user_id]['step'] == 100 or not self.user_task_data[user_id]['wait'].__contains__(id):  # 断开的车不是此任务包含的车
                continue
            if not self.user_task_data[user_id]['shellback'].__contains__(id):
                self.user_task_data[user_id]['shellback'].append(id)
            if self.user_task_data[user_id]['path'].__contains__(id):  # ==''表示车上没有压完文件，就断开了
                if self.task_user_.__contains__(self.user_task_data[user_id]['task']):
                    if self.user_task_data[user_id]['path'][id] == 'null':  # 该车已经返回无数据，已经处理
                        continue
                    elif self.user_task_data[user_id]['path'][id] == 'ftpnull':  # 已经pull文件失败，已经处理
                        continue
                    elif self.user_task_data[user_id]['path'][id] == '':  # 该车之前没有任何处理
                        pass
                    else:  # 该车已经正常返回文件名，若还没拉取，后面会处理
                        continue
                    if not self.user_task_data[user_id]['failed'].__contains__(id):
                        self.user_task_data[user_id]['failed'].append(id)
                    if self.user_task_data[user_id]['success'].__contains__(id):
                        self.user_task_data[user_id]['success'].remove(id)
                    self.user_task_data[user_id]['err'] = BlackboxDisconnect
                    self.failed_get_log(user_id)
                    continue
            else:
                continue
        print('mutes-dis-release-0')
        self.mutex.release()
    # 收到车上shell压缩的文件，返回的车上路径
    def load_log_path(self,id, stat, data,pkt_err):
        print('back----', stat,id,data,self.user_task_data)
        global notify_step_function
        if stat == -1 and data == '':  # shell此时断连的话
            self.is_disconnect(id)
            return

        Logger().get_logger().info("{0} shell back,error type is {1}".format(id,pkt_err))
        path = log.proto_logs_file_path()
        path.build(data, 0)
        if not self.task_user_.__contains__(int(path.task_id)) :
            return
        user_id = self.task_user_[int(path.task_id)]
        print('mutes-load-acquire-0')
        self.mutex.acquire()
        if self.user_task_data[user_id]['status']==1:
            self.mutex.release()
            return
        self.user_task_data[user_id]['err'] = pkt_err
        if not self.user_task_data[user_id]['shellback'].__contains__(id):
            self.user_task_data[user_id]['shellback'].append(id)
        if len(path.vct_log_file_name) == 0:  # 没有文件返回
            if pkt_err==0:
                self.user_task_data[user_id]['err']=BlackboxNoLog
            Logger().get_logger().warning('not find any log files :by user {0} robot id:{1}'.format(user_id, id))
            self.user_task_data[user_id]['path'][id] = 'null'
            if not self.user_task_data[user_id]['failed'].__contains__(id):
                self.user_task_data[user_id]['failed'].append(id)
            if self.user_task_data[user_id]['success'].__contains__(id):
                self.user_task_data[user_id]['success'].remove(id)
            self.failed_get_log(user_id)
            print('mutes-load-release-0')
            self.mutex.release()
            return

        if len(path.vct_log_file_name) != 0 and path.task_id==self.user_task_data[user_id]['task']:
            print('id_log_path', id, path.vct_log_file_name[0])
            # fts去取压缩好的文件
            strpath = path.vct_log_file_name[0].value
            local_path = str(id) + '_' + strpath[strpath.rfind('/') + 1:]#self.get_user_tmp_path(user_id) +
            self.user_task_data[user_id]['path'][id] = local_path
            print('local_tmp_path', local_path)
            route_path_list = [{'robot_id': id, 'file_path': path.vct_log_file_name[0].value, 'local_path': self.get_user_tmp_path(user_id) +local_path}]
            err,task = pull_file_from_remote(user_id, FILE_TYPE_BLACKBOX_PULL_FILES, route_path_list)
            if len(task) > 0:
                print('pull file err 0')
                self.user_task_data[user_id]['pull_list'].append(task[0]['task_id'])
            else:
                Logger().get_logger().info('file_rw task list is full')
                self.user_task_data[user_id]['err'] = BlackboxPullFailed
                self.fts_err_status(user_id,id)
        print('mutes-load-release-0.1')
        self.mutex.release()

    # 压缩文件
    # def tar_threading_func(self):
    #     global notify_step_function,thread_wait
    #     while True:
    #         print('start wait')
    #         thread_wait.wait(0xffffffff)
    #         print('tar_list1:', self.tar_list)
    #
    #         while True:
    #             self.tar_mutex.acquire()
    #             if len(self.tar_list)<=0:
    #                 self.tar_mutex.release()
    #                 break
    #             tar_tmp=deepcopy(self.tar_list[0])
    #             del self.tar_list[0]
    #             self.tar_mutex.release()
    #             print('tar_list2:', tar_tmp)
    #             user_id=tar_tmp['user']
    #             file_path = tar_tmp['path']
    #
    #             open_path = self.get_user_tmp_path(user_id)
    #             zip_file = self.get_user_path(user_id) + self.user_task_data[int(user_id)]['name']
    #             zip_file_tmp = open_path + self.user_task_data[user_id]['name']
    #             if self.user_task_data[int(user_id)]['handle'] is not None:
    #                 handle = self.user_task_data[user_id]['handle']
    #
    #
    #             if file_path=='last':
    #                 handle.close()
    #                 print('close task')
    #                 shutil.move(zip_file_tmp, zip_file)
    #                 if os.path.exists(open_path):
    #                     shutil.rmtree(open_path)
    #             else:
    #                 print('write------', file_path, open_path, self.tar_list)
    #                 Logger().get_logger().info('tar log')
    #                 filefullpath = os.path.join(open_path, file_path)
    #                 if os.path.isfile(filefullpath):
    #                     if os.path.isfile(zip_file_tmp):#防止文件被删除
    #                         handle.add(filefullpath, arcname=file_path)
    #                         if self.user_task_data[user_id]['delete']==1:
    #                             self.user_task_data[user_id]['handle'].close()
    #                             self.delete_tmp_file(user_id)
    #                             self.delete_log(user_id, self.user_task_data[user_id]['name'])
    #                             del self.task_user_[self.user_task_data[user_id]['task']]
    #                             del self.user_task_data[user_id]
    #                         Logger().get_logger().info('tar log 1')
    #
    #                 task_curr=0
    #                 self.tar_mutex.acquire()
    #                 for item in self.tar_list:
    #                     if item['user']==user_id:
    #                         task_curr+=1
    #                 self.tar_mutex.release()
    #
    #                 if self.user_task_data[int(user_id)]['step'] == 100 and task_curr==0:
    #                     handle.close()
    #                     print('close task')
    #                     shutil.move(zip_file_tmp, zip_file)
    #                     if os.path.exists(open_path):
    #                         shutil.rmtree(open_path)
    #                     if notify_step_function is not None:
    #                         notify_step_function(user_id,{'step': 100, 'msg_type': errtypes.TypeShell_BlackboxLog,
    #                                           'task_id': self.user_task_data[user_id]['task']})
    #                 Logger().get_logger().info('tar log over')

    # pull文件时，回调进度
    def pull_log_step_notify(self,user_id, robot_id, step, file_path, error_code,status):  # file_path需要改成保存后台的文件名,status状态表示file_rw推拉是否正常
        global notify_step_function ,thread_wait
        if file_path=='':
            #最后一个断线or没有文件，
            print('mutes-pull-acquire-0')
            self.mutex.acquire()
            self.user_task_data[int(user_id)]['step'] = 100
            task_tar = threading.Thread(target=backup_manage.task_over_tar_log_file, args=(self, user_id))
            task_tar.setDaemon(True)
            task_tar.start()
            print('mutes-pull-release-0')
            self.mutex.release()

            #notify_step_function(user_id,{'step': 100, 'msg_type': errtypes.TypeShell_BlackboxLog, 'task_id': self.user_task_data[user_id]['task']})
            return
        print('step', step, error_code, status)
        if step == 100 and status == 1:
            print('mutes-pull-acquire-1')
            self.mutex.acquire()
            if not self.user_task_data[user_id]['success'].__contains__(robot_id):
                self.user_task_data[user_id]['success'].append(robot_id)
            if self.user_task_data[user_id]['pull_list'].__contains__(robot_id):
                self.user_task_data[user_id]['pull_list'].remove(robot_id)
            tmp = str(robot_id) + '_' + file_path[file_path.rfind('/') + 1:]
            if len(self.user_task_data[user_id]['success'])+len(self.user_task_data[user_id]['failed'])==len(self.user_task_data[user_id]['wait']):
                self.user_task_data[int(user_id)]['step'] = 100
                task_tar = threading.Thread(target=backup_manage.task_over_tar_log_file, args=(self,user_id))
                task_tar.setDaemon(True)
                task_tar.start()
            print('mutes-pull-release-1')
            self.mutex.release()


        if error_code != 0:
            print('mutes-pull-acquire-2')
            self.mutex.acquire()
            self.user_task_data[user_id]['err'] = BlackboxPullFailed
            self.fts_err_status(user_id,robot_id)
            print('mutes-pull-release-2')
            self.mutex.release()
            if not self.user_task_data.__contains__(user_id):
                return

        print('mutes-pull-acquire-3')
        self.mutex.acquire()
        print('len-',len(self.user_task_data[user_id]['success']),len(self.user_task_data[user_id]['failed']),len(self.user_task_data[user_id]['wait']))
        if len(self.user_task_data[user_id]['success'])+len(self.user_task_data[user_id]['failed'])==len(self.user_task_data[user_id]['wait']):
            pass
        else:
            if step == 100 and status == 1:
                sch=100*(len(self.user_task_data[user_id]['success'])+len(self.user_task_data[user_id]['failed']))//len(self.user_task_data[user_id]['wait'])# 总进度
            else:
                sch = (100 * (len(self.user_task_data[user_id]['success']) + len(self.user_task_data[user_id]['failed']))+step) // len(self.user_task_data[user_id]['wait'])# 总进度
            if sch>self.user_task_data[int(user_id)]['step'] and notify_step_function is not None:

                self.user_task_data[int(user_id)]['step'] = sch
                notify_step_function(user_id,{'step': sch, 'msg_type': errtypes.TypeShell_BlackboxLog,
                                          'task_id': self.user_task_data[user_id]['task']})
        print('mutes-pull-release-3')
        self.mutex.release()

    def fts_err_status(self,user_id,robot_id):
        print('mutes-ftserr-acquire-0')
        global notify_step_function
        self.mutex.acquire()
        self.user_task_data[user_id]['path'][robot_id] = 'ftpnull'
        if not self.user_task_data[user_id]['failed'].__contains__(robot_id):
            self.user_task_data[user_id]['failed'].append(robot_id)
        print('data:',self.user_task_data[user_id])
        if len(self.user_task_data[user_id]['failed']) == len(self.user_task_data[user_id]['wait']):
            if len(self.user_task_data[user_id]['wait'])==1 and self.user_task_data[user_id]['err']==BlackboxPullFailed:
                if notify_step_function is not None:
                    notify_step_function(user_id, {'msg_type': errtypes.TypeShell_BlackboxFailed,'task_id': self.user_task_data[user_id]['task'],'err_type':BlackboxPullFailed})
            else:
                if notify_step_function is not None:
                    notify_step_function(user_id,{'msg_type': errtypes.TypeShell_BlackboxFailed,'task_id':self.user_task_data[user_id]['task'],'err_type':BlackboxFailed})
            self.delete_tmp_file(user_id)
            self.delete_log(user_id, self.user_task_data[user_id]['name'])
            del self.task_user_[self.user_task_data[user_id]['task']]
            del self.user_task_data[user_id]
            print('mutes-ftserr-acquire-0.1')
            self.mutex.release()
            print('over-103',self.user_task_data)
            return

        if len(self.user_task_data[user_id]['success']) + len(self.user_task_data[user_id]['failed']) == len(self.user_task_data[user_id]['wait']) and \
                len(self.user_task_data[user_id]['failed']) != len(self.user_task_data[user_id]['wait']):
            self.user_task_data[int(user_id)]['step'] = 100
            print('mutes-ftserr-acquire-0.2')
            self.mutex.release()
            task_tar = threading.Thread(target=backup_manage.task_over_tar_log_file, args=(self, user_id))
            task_tar.setDaemon(True)
            task_tar.start()
            #notify_step_function(user_id,{'step': 100, 'msg_type': errtypes.TypeShell_BlackboxLog,'task_id': self.user_task_data[user_id]['task']})

    def send_step_websocket(self,user_id):
        global notify_step_function
        self.mutex.acquire()
        sch = 100 * (len(self.user_task_data[user_id]['success']) + len(self.user_task_data[user_id]['failed'])) // len(
            self.user_task_data[user_id]['wait'])  # 总进度
        if notify_step_function is not None:
            notify_step_function(user_id, {'step': sch, 'msg_type': errtypes.TypeShell_BlackboxLog,'task_id': self.user_task_data[user_id]['task']})
        self.mutex.release()

    def register_blackbox_step_notify(self,log_notify=None):
        global notify_step_function
        notify_step_function = log_notify

    #获取失败or断连
    def failed_get_log(self,user_id):
        print('count-',len(self.user_task_data[user_id]['success']),len(self.user_task_data[user_id]['wait']),len(self.user_task_data[user_id]['failed']))
        global notify_step_function
        print('mutes-failed-acquire-0')
        self.mutex.acquire()
        if len(self.user_task_data[user_id]['failed'])==len(self.user_task_data[user_id]['wait']):
            if len(self.user_task_data[user_id]['failed'])==1:
                err_type=0
                if self.user_task_data[user_id]['err']==BlackboxNoLog :
                    err_type=BlackboxNoLog
                elif self.user_task_data[user_id]['err']==BlackboxTarFailed:
                    err_type = BlackboxTarFailed
                elif self.user_task_data[user_id]['err']==BlackboxDisconnect:
                    err_type = BlackboxDisconnect
                if notify_step_function is not None:
                    notify_step_function(user_id, {'msg_type': errtypes.TypeShell_BlackboxFailed,'task_id': self.user_task_data[user_id]['task'],'err_type':err_type})
            else:
                if notify_step_function is not None:
                    notify_step_function(user_id,{'msg_type': errtypes.TypeShell_BlackboxFailed,'task_id':self.user_task_data[user_id]['task'],'err_type':-1})
            self.user_task_data[user_id]['handle'].close()
            self.delete_log(user_id, self.user_task_data[user_id]['name'])
            self.delete_tmp_file(user_id)
            del self.task_user_[self.user_task_data[user_id]['task']]
            del self.user_task_data[user_id]
            print('mutes-failed-release-0.1')
            self.mutex.release()
            return -1
        elif len(self.user_task_data[user_id]['success'])+len(self.user_task_data[user_id]['failed'])==len(self.user_task_data[user_id]['wait']) and len(self.user_task_data[user_id]['failed'])!=len(self.user_task_data[user_id]['wait']):
            self.pull_log_step_notify(user_id, id, 100, '', 0, 1)  # 最后一个断线或失败 且 不是全部断线失败有，成功的
            print('mutes-failed-release-0.2')
            self.mutex.release()
            return 0
        elif len(self.user_task_data[user_id]['success'])+len(self.user_task_data[user_id]['failed'])!=len(self.user_task_data[user_id]['wait']):
            self.send_step_websocket(user_id)

        print('mutes-failed-release-0.3')
        self.mutex.release()


    # 获取存后台的路径
    def get_user_path(self,user_id):
        user_name = self.__userid_to_name[user_id]
        folder_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER
        if os.path.exists(folder_path) == False:
            os.makedirs(folder_path)
        return folder_path

    def get_user_tmp_path(self,user_id):
        user_name = self.__userid_to_name[user_id]
        tmp_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER + 'tmp/'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        return tmp_path

    # 获取后台要下载文件的全路径
    def exists_log(self,user_id, log_name):
        (ret,user_name) =user.query_name_by_id(user_id)
        if -1==ret:
            return -3 #用户不存在
        if -2==ret:
            return -4 #数据错误

        folder_path = config.ROOTDIR + user_name + config.BLACKBOXFOLDER
        if os.path.exists(folder_path) == False:
            return -1#没有文件夹
        list = os.listdir(folder_path)
        for index in list:
            if os.path.isfile(folder_path + index) and os.path.splitext(index)[1] == ".tar" and os.path.join(folder_path + log_name) == os.path.join(folder_path + index):
                return 0
        return -2#没有文件




    #文件pull完才开始tar文件
    def task_over_tar_log_file(self,user_id):
        global notify_step_function
        if self.user_task_data.__contains__(user_id):
            self.mutex.acquire()
            self.user_task_data[user_id]['tar'] = 0
            tmp_task=self.user_task_data[user_id]
            self.mutex.release()
            handle = tmp_task['handle']
            open_path = self.get_user_tmp_path(user_id)
            zip_file = self.get_user_path(user_id) + tmp_task['name']
            zip_file_tmp = open_path + tmp_task['name']
            for index in tmp_task['success']:
                if tmp_task['path'].__contains__(index):
                    file_path=tmp_task['path'][index]
                    filefullpath = os.path.join(open_path, file_path)
                    if os.path.exists(filefullpath):
                        if os.path.isfile(zip_file_tmp):  # 防止文件被删除
                            handle.add(filefullpath, arcname=file_path)
                            if tmp_task['delete'] == 1:  #在压缩时如果已经在压缩，待压缩完删除文件和任务
                                tmp_task['handle'].close()
                                self.delete_tmp_file(user_id)
                                self.delete_log(user_id, tmp_task['name'])
                                del self.task_user_[tmp_task['task']]
                                self.mutex.acquire()
                                del self.user_task_data[user_id]
                                self.mutex.release()
                                return
                            Logger().get_logger().info('tar log 1')
            handle.close()
            print('close task')
            self.mutex.acquire()
            self.user_task_data[user_id]['tar'] = 1
            self.mutex.release()
            file_size = os.path.getsize(zip_file_tmp)
            ret=file_manager.insert(user_id,tmp_task['name'],file_size)

            shutil.move(zip_file_tmp, zip_file)
            print('path--',zip_file_tmp, zip_file)
            if os.path.exists(open_path):
                shutil.rmtree(open_path)
            if ret == 0:
                if notify_step_function is not None:
                    notify_step_function(user_id,{'step': 100, 'msg_type': errtypes.TypeShell_BlackboxLog,'task_id': tmp_task['task']})
                Logger().get_logger().info('tar log over')
            else:#插数据库失败
                self.delete_tmp_file(user_id)
                self.delete_log(user_id, tmp_task['name'])
                del self.task_user_[tmp_task['task']]
                self.mutex.acquire()
                del self.user_task_data[user_id]
                self.mutex.release()
                Logger().get_logger().info('inster sql failed ,err:{0}',format(ret))
                if notify_step_function is not None:
                    notify_step_function(user_id,{'msg_type': errtypes.TypeShell_BlackboxFailed,'task_id': tmp_task['task'],'err_type':BlackboxInsertSqlFaild})







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