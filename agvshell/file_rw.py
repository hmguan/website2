# -*- coding: utf-8 -*- 
import os
import sys
import time
import datetime
import threading
import queue
import shutil
from .shproto.errno import *
from pynsp.logger import *
from pynsp import singleton as slt
from pynsp.wait import *
import errtypes
from copy import deepcopy
from .transfer_file_types import *

#file_status
FILE_STATUS_TIMEOUT = -5
FILE_STATUS_CANCLE = -4
FILE_STATUS_UNINIT = -3
FILE_STATUS_READ_ERROR = -2
FILE_STATUS_WRITE_ERROR = -1
FILE_STATUS_NORMAL = 0
FILE_STATUS_COMPLETE = 1

#文件传输并发数 
MAX_THREAD_NUM = 1
#最大任务数 
MAX_QUEUE_NUM = 1000

#<key:robot_id, value:<file_id, file_info> >
dict_file_info={}
#全局数据锁  
file_mutex=threading.RLock()
#dict for upgrade 


class base_task():
    '''
    basic task definition
    task used to execute by task pool
    '''
    def __init__(self):
        pass
        
    def on_task(self,id):
        """
        virtual function.
        handle your protocol with overwrite this method.
        """
        print("base_task ", id)
        return -1
        pass

class task_thread_pool():
    '''
    definition a threads pool to execute task
    thread num is define by global MAX_THREAD_NUM
    '''
    def __init__(self):
        self.__work_queue = list()
        self.__working_queue = list()
        self.__queue_mutex=threading.RLock()
        self.__work_threads = []
        self.__thread_wait = waitable_handle(False)
        self.__exit_flag = 0
        self.__is_working = {}
        self.init_pool()
        
    def __del__(self):
        self.__exit_flag = 1
        self.thread_join()
        self.__queue_mutex.acquire()
        self.__work_queue.clear()
        self.__working_queue.clear()
        self.__queue_mutex.release()
        
    def init_pool(self):
        if len(self.__work_threads) > 0:
            return -1
            
        for i in range(MAX_THREAD_NUM):
            t_th = threading.Thread(target=task_thread_pool.th_handler,args=(self,i,))
            t_th.setDaemon(True)
            t_th.start()
            self.__work_threads.append(t_th)
            pass
    
    def th_handler(self,id):
        thread_id = id
        self.__is_working[thread_id] = False
        while 0 == self.__exit_flag:
            if self.__is_working[thread_id]:
                time.sleep(2)
                continue

            self.__queue_mutex.acquire()
            while 0 == len(self.__work_queue):
                self.__queue_mutex.release()
                print("thread:%d waiting" % thread_id)
                self.__thread_wait.wait()
                self.__thread_wait.reset()
                print("thread:%d wake up" % thread_id)
                if self.__exit_flag > 0:
                    return
                self.__queue_mutex.acquire()
                
            task = self.__work_queue.pop(0)
            self.__working_queue.append({'thread_id':thread_id,'task_info':task})

            Logger().get_logger().info('thread:{} start task, queue size:{}'.format(thread_id,len(self.__work_queue)))
            self.__is_working[thread_id] = True
            self.__queue_mutex.release()
            ret = task.on_task(thread_id)
            Logger().get_logger().info('thread:{} after on_task ret{}'.format(thread_id,ret))
        Logger().get_logger().info('thread id:{} exit'.format(thread_id))  
        
    def add_task(self,task):
        self.__queue_mutex.acquire()
        if len(self.__work_queue) >= MAX_QUEUE_NUM:
            Logger().get_logger().error('task queue full!!!') 
            return -1
        self.__work_queue.append(task)
        self.__queue_mutex.release()
        self.__thread_wait.sig()
        pass
        
    def del_task(self,count,callback):
        '''
        specile for file_task
        '''
        del_task = []
        self.__queue_mutex.acquire()
        if count > 0 and callback :
            for item in list(self.__work_queue):
                if callback(item):
                    del_task.append(item)
                    self.__work_queue.remove(item)
                    count = count -1
                    if count == 0:
                        break
        self.__queue_mutex.release()
        return del_task
    
    def task_finish(self,thread_id,task_id):
        self.__is_working[thread_id] = False
        self.__queue_mutex.acquire()
        for transfer_task in self.__working_queue:
            if transfer_task['thread_id'] == thread_id:
                self.__working_queue.remove(transfer_task)
                break
        self.__queue_mutex.release()
        Logger().get_logger().info("thread[{}] working status change".format(thread_id)) 
        pass

    def thread_join(self):
        self.__thread_wait.sig()
        for th in self.__work_threads:
            th.join()
        pass

    def Query_Transfer_queue(self):
        self.__queue_mutex.acquire()
        queue = deepcopy(self.__work_queue)
        for index,task in enumerate(self.__working_queue):
            queue.insert(index,task['task_info'])
        self.__queue_mutex.release()
        return queue

    def get_queue_size(self):
        return len(self.__work_queue) + len(self.__working_queue)


class agvfile():
    def __init__(self):
        
        pass

    def __del__(self):
        pass

    def create_file(self,name):
        try:
            fd = open(name, 'wb')
        except IOError:
            Logger().get_logger().error("create_file file {} failure".format(name)) 
            return -1
        else:
            Logger().get_logger().info("create_file file {} success".format(name)) 
            return fd

    def open_file(self,name):
        try:
            fd=open(name, 'rb')
        except IOError:
            Logger().get_logger().error("open_file file {} failure".format(name)) 
            return -1
        else:
            Logger().get_logger().info("open_file file {} success".format(name)) 
            return fd
    
    def read_file(self,fd,off,len):
        try:
            fd.seek(off)
            data=fd.read(len)
            #print("read len[%d] data[%s]" % (len, data))
        except IOError:
            print("write file error")
            return ""
        else:
            return data
    
    def write_file(self,fd,off,len,data):
        try:
            fd.seek(off)
            fd.write(data)
            #print("write len[%d] data to off[%d]" % (len, off))
        except:
            print("write file error")
            return -1
        else:
            return 0
    
    #循环遍历删除 @path 下的内容  
    def del_path(self,path):
        shutil.rmtree(path)
        

    def get_file_attr(self,path):
        file_size = os.path.getsize(path) #filePath = unicode(filePath,'utf8')
        ctime = os.path.getctime(path)
        atime = os.path.getatime(path)
        mtime = os.path.getmtime(path)
        return file_size,ctime,atime,mtime
    
    def set_file_attr(self, path, atime, ctime, mtime):
        os.utime(path, (atime, mtime))
        return 0


class file_task(base_task):
    def __init__(self,s_user_id,r_id,f_path,f_type,oper_type,task_id,local_path = "",packageId = -1):
        self.m_session_uid = 0
        self.m_user_id= s_user_id
        self.m_robot_id = r_id
        self.m_file_path = f_path
        self.m_file_type = f_type
        self.m_oper_type = oper_type
        self.m_task_id = task_id
        self.m_local_path = local_path
        self.m_package_id = packageId
    
    def on_task(self,thread_id):
        ret = -1
        if FILE_OPER_TYPE_PUSH == self.m_oper_type:
            ret = file_manager().push_file(thread_id,self.m_user_id,self.m_robot_id,self.m_file_path,self.m_file_type,self.m_task_id)
        elif FILE_OPER_TYPE_PULL == self.m_oper_type:
            ret = file_manager().pull_file(thread_id,self.m_user_id,self.m_robot_id,self.m_file_path,self.m_file_type,self.m_task_id,self.m_local_path)
        else:
            pass
        return ret

        
class file_info():
    def __init__(self):
        self.m_file_id=0
        self.m_name=""
        self.m_path=""
        self.m_type=0
        self.m_hd=None
        self.m_size=0
        self.m_block_num=0
        self.m_last_block_num=0
        self.m_last_off=0
        self.m_ctime=0
        self.m_atime=0
        self.m_mtime=0
        self.m_oper_time=0
        self.m_oper_type=0
        self.m_session_uid=0
        self.m_thread_uid=0
        self.m_user_id = 0
        self.m_step = 0         #传输进度
        self.m_task_id = 0
        self.m_block_size = 32*1024

    def __del__(self):
        if self.m_hd is not None and -1 != self.m_hd:
            self.m_hd.close()

class user_transfer_queue(object):
    """docstring for user_transfer_queue"""
    def __init__(self,assign_task_cb):
        super(user_transfer_queue, self).__init__()
        self.__task_thread_pool_push = None
        self.__task_thread_pool_pull = None
        self.__task_id = 0
        self.__assign_task_cb = assign_task_cb


    def assign_task_id(self):
        self.__task_id = self.__task_id+1
        return self.__task_id

    def __del__(self):
        pass

    def task_finish(self,threadid,task_id = -1,transfer_type = -1,):
        if transfer_type != -1 and task_id != -1:
            # self.__thread_upgrade_mutex.acquire()
            if transfer_type == FILE_OPER_TYPE_PUSH:
                if self.__task_thread_pool_push is not None:
                    self.__task_thread_pool_push.task_finish(threadid,task_id)
            elif transfer_type == FILE_OPER_TYPE_PULL:
                if self.__task_thread_pool_pull is not None:
                    self.__task_thread_pool_pull.task_finish(threadid,task_id)
            # self.__thread_upgrade_mutex.release()

    def push_file_task(self,user_id,robot_list,file_path,file_type,packet_id):
        '''
        push 'push file task to task pool'
        '''
        err_robot = []
        task_list = []
        task_id = 0
        # self.__thread_upgrade_mutex.acquire()
        for item in robot_list:
            robot_id = int(item)

            if self.__assign_task_cb:
                task_id = self.__assign_task_cb()
            else:
                task_id = self.assign_task_id()
            
            task = file_task(user_id,robot_id,file_path,file_type,FILE_OPER_TYPE_PUSH,task_id,"",packet_id)
            if self.__task_thread_pool_push is None:
                self.__task_thread_pool_push = task_thread_pool()
            if self.__task_thread_pool_push.add_task(task) != -1 :
                task_list.append({'robot_id':robot_id,'task_id':task_id})
            else:
                err_robot.append(robot_id)
        # self.__thread_upgrade_mutex.release()

        return task_list , err_robot

    def pull_file_task(self,userid,file_type,route_path_list):
        err_robot = []
        task_list = []
        task_id = 0
        for item in route_path_list:

            if self.__assign_task_cb:
                task_id = self.__assign_task_cb()
            else:
                task_id = self.assign_task_id()

            if self.__task_thread_pool_pull is None:
                self.__task_thread_pool_pull = task_thread_pool()
            task = file_task(userid,item['robot_id'],item['file_path'],file_type,FILE_OPER_TYPE_PULL,task_id,item['local_path'])
            if self.__task_thread_pool_pull.add_task(task) != -1 :
                task_list.append({'robot_id':item['robot_id'],'task_id':task_id,'file_path':item['file_path']})
            else:
                err_robot.append(item['robot_id'])
        return task_list , err_robot

    def get_transfer_queue(self,file_oper_type):
        if file_oper_type == FILE_OPER_TYPE_PUSH:
            if self.__task_thread_pool_push:
                return self.__task_thread_pool_push.Query_Transfer_queue()
        elif file_oper_type == FILE_OPER_TYPE_PULL:
            if self.__task_thread_pool_pull :
                return self.__task_thread_pool_pull.Query_Transfer_queue()
        return 0
        

    def get_transfer_num(self):
        task_push_num = 0
        task_pull_num = 0
        if self.__task_thread_pool_push:
            task_push_num = self.__task_thread_pool_push.get_queue_size()
        if self.__task_thread_pool_pull:
            task_pull_num = self.__task_thread_pool_pull.get_queue_size()

        return task_pull_num + task_push_num

    def del_task(self,count, callback):
        del_push_task = list()
        del_pull_task = list()
        if self.__task_thread_pool_push:
            del_push_task = self.__task_thread_pool_push.del_task(count,callback)
        if self.__task_thread_pool_pull and count > len(del_push_task):
            del_pull_task = self.__task_thread_pool_pull.del_task(count - len(del_push_task),callback)
        return list(set(del_push_task).union(set(del_pull_task)))

@slt.singleton
class file_manager():
    def __init__(self):
        self.__file_id=0
        self.__file_id_mutex=threading.RLock()
        self.__file_rw = agvfile()
        self.__file_dir = "./"
        self.__block_size = int(32 * 1024) #default 32k
        self.__notify_callback = None
        self.__shell_manager = None
        # user transmission queue
        # user_id : thread pool
        self.__transfer_queue_mutex = threading.RLock()
        self.__map_user_transfer_queue = dict()
        #upgrading set
        self.__mutex_set = threading.RLock()
        self.__task_id = 0
        self.__task_id_mutex=threading.RLock()

    def assign_task_id(self):
        self.__task_id_mutex.acquire()
        self.__task_id = self.__task_id +1
        self.__task_id_mutex.release()
        return self.__task_id

    def __del__(self):
        pass

    def notify(self,userid, robot_id, file_path, file_type, step, error_code, status, task_id,file_size = 0):
        if self.__notify_callback is not None:
            self.__notify_callback(userid,robot_id,file_path,file_type,step,error_code,status,task_id,file_size)

    def allocate_file_id(self):
        self.__file_id_mutex.acquire()
        self.__file_id += 1
        self.__file_id_mutex.release()
        return self.__file_id

    def get_block_size(self) ->int:
        from configuration import config
        try:
            return int(config.TRANSMIT_BLOCK_SIZE)
            pass
        except Exception as e:
            return int(self.__block_size)

    def add_file_info(self,t_file_info,robot_id):
        # file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            map_file_info = {}
            map_file_info[t_file_info.m_file_id] = t_file_info
            dict_file_info[robot_id] = map_file_info
        else:
            map_file_info[t_file_info.m_file_id] = t_file_info
        # file_mutex.release()

    def remove_file_info(self,robot_id,file_id):
        # file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is not None:
            if file_id in map_file_info:
                del map_file_info[file_id]
            if len(map_file_info) == 0:
                del dict_file_info[robot_id]
        # file_mutex.release()

    def task_finish(self,user_id,thread_id,task_id,transfer_type):
        self.__transfer_queue_mutex.acquire()
        user_transfer_queue = self.__map_user_transfer_queue.get(user_id)
        if user_transfer_queue is not None:
            user_transfer_queue.task_finish(thread_id,task_id,transfer_type)
            if user_transfer_queue.get_transfer_num() == 0:
                del self.__map_user_transfer_queue[user_id]
        self.__transfer_queue_mutex.release()

    def query_transfer_queue(self,user_id,oper_type) ->list:
        queue_data = []
        user_transfer_queue = self.__map_user_transfer_queue.get(user_id)
        if user_transfer_queue is not None:
            transfer_queue = user_transfer_queue.get_transfer_queue(oper_type)
            for transfer_info in transfer_queue:
                queue_data.append({'robot_id':transfer_info.m_robot_id,'packet_id':transfer_info.m_package_id,'file_type':transfer_info.m_file_type,'task_id':transfer_info.m_task_id})
        return queue_data


    def query_file_queue_used(self)->set:
        file_mutex.acquire()
        list_file_path = [ file_info for value in list(dict_file_info.values()) for file_info in list(value.values()) if file_info.m_type == FILE_OPER_TYPE_PUSH]
        file_mutex.release()
        file_path_set = set()
        for item in list_file_path:
            if item.m_path not in file_path_set:
                file_path_set.add(item.m_path)
        Logger().get_logger().info("file_path_set{} file is busy".format(file_path_set)) 
        return file_path_set

    def push_file(self,threadID,m_userid,robot_id,file_path,file_type,task_id):
        if self.__shell_manager is None:
            Logger().get_logger().error("shell manager regist failure, robot_id{}".format(robot_id)) 
            self.notify(m_userid,robot_id,file_path,file_type,0,ERRNO_ROBOT_CONNECT,-1,task_id)
            self.task_finish(m_userid,threadID,task_id,FILE_OPER_TYPE_PUSH)
            return ERRNO_ROBOT_CONNECT
        
        shell_info = self.__shell_manager.get_session_by_id(robot_id)
        if shell_info is None:
            Logger().get_logger().error("session cannot find, robot_id{}".format(robot_id)) 
            self.notify(m_userid,robot_id,file_path,file_type,0,ERRNO_ROBOT_CONNECT,-1,task_id)
            self.task_finish(m_userid,threadID,task_id,FILE_OPER_TYPE_PUSH)
            return ERRNO_ROBOT_CONNECT

        # 正在升级的车辆进行拒绝
        if FILE_TYPE_A_UPGRADE == file_type:
            self.__mutex_set.acquire()
            if FILE_TYPE_A_UPGRADE == shell_info.get_upgrade_flag():
                print("upgrade exit, stop this time upgrade")
                self.__mutex_set.release()
                self.notify(m_userid,robot_id,file_path,file_type,0,ERRNO_FILE_UPGRADE,-1,task_id)
                self.task_finish(m_userid,threadID,task_id,FILE_OPER_TYPE_PUSH)
                return ERRNO_FILE_UPGRADE
            shell_info.set_upgrade(FILE_TYPE_A_UPGRADE)
            self.__mutex_set.release()

        t_file_info = file_info()
        t_file_info.m_hd = self.__file_rw.open_file(file_path)
        if -1 == t_file_info.m_hd:
            Logger().get_logger().error("open file[{}] failure".format(file_path))
            self.notify(m_userid,robot_id,file_path,file_type,0,ERRNO_FILE_OPEN,-1,task_id)
            self.task_finish(m_userid,threadID,task_id,FILE_OPER_TYPE_PUSH)
            return ERRNO_FILE_OPEN
           
        t_file_info.m_type = file_type
        t_file_info.m_path = file_path
        t_file_info.m_name = file_path[file_path.rfind('/') + 1:]
        t_file_info.m_file_id = self.allocate_file_id()
        t_file_info.m_size,t_file_info.m_ctime,t_file_info.m_atime,t_file_info.m_mtime = self.__file_rw.get_file_attr(file_path)
        
       
        t_file_info.m_oper_time = int(round(time.time() * 1000))
        t_file_info.m_oper_type = FILE_OPER_TYPE_PUSH
        t_file_info.m_user_id = m_userid
        t_file_info.m_thread_uid = threadID
        t_file_info.m_last_block_num = 0
        t_file_info.m_last_off = 0
        t_file_info.m_task_id = task_id
        t_file_info.m_block_size = self.get_block_size()
        t_file_info.m_block_num = int(t_file_info.m_size / t_file_info.m_block_size)
        if t_file_info.m_size % t_file_info.m_block_size > 0:
            t_file_info.m_block_num += 1
        self.add_file_info(t_file_info,robot_id)

        #这里不对发送数据失败进行处理 统一在心跳中处理
        shell_info.push_file_head(t_file_info.m_file_id,t_file_info.m_type,t_file_info.m_name,t_file_info.m_size, \
                (t_file_info.m_ctime+11644473600)*10000000,(t_file_info.m_atime+11644473600)*10000000,(t_file_info.m_mtime+11644473600)*10000000) 
        self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,0,0,0,t_file_info.m_task_id,t_file_info.m_size)
        Logger().get_logger().info('push file head secuss, name:{0} size:{1}, block_num: {2}'.format(t_file_info.m_path, t_file_info.m_size, t_file_info.m_block_num))
        return 0
    
    def pull_file(self,threadID,userid,robot_id,file_path,file_type,taskId,localpath):
        if file_path == "":
            self.notify(userid,robot_id,file_path,file_type,0,ERRNO_FILE_OPEN,-1,taskId)
            self.task_finish(userid,threadID,taskId,FILE_OPER_TYPE_PULL)
            return ERRNO_FILE_OPEN
        
        if self.__shell_manager is None:
            print("shell manager regist failure, robot_id:%d" % robot_id)
            self.notify(userid,robot_id,file_path,file_type,0,ERRNO_ROBOT_CONNECT,-1,taskId)
            self.task_finish(userid,threadID,taskId,FILE_OPER_TYPE_PULL)
            return ERRNO_ROBOT_CONNECT
        
        shell_info = self.__shell_manager.get_session_by_id(robot_id)
        if shell_info is None:
            print("session cannot find, robot_id:%d" % robot_id)
            self.notify(userid,robot_id,file_path,file_type,0,ERRNO_ROBOT_CONNECT,-1,taskId)
            self.task_finish(userid,threadID,taskId,FILE_OPER_TYPE_PULL)
            return ERRNO_ROBOT_CONNECT
        
        t_file_info = file_info()
        t_file_info.m_name = localpath
        t_file_info.m_path = file_path
        t_file_info.m_type = file_type
        t_file_info.m_file_id = self.allocate_file_id()
        t_file_info.m_oper_time = int(round(time.time() * 1000))
        t_file_info.m_oper_type = FILE_OPER_TYPE_PULL
        t_file_info.m_user_id = userid
        t_file_info.m_thread_uid = threadID
        t_file_info.m_task_id = taskId

        self.add_file_info(t_file_info,robot_id)

        shell_info.pull_file_head(t_file_info.m_file_id,file_path)

        Logger().get_logger().info('begin to pull file:{0}, file id:{1}'.format(t_file_info.m_name, t_file_info.m_file_id))
        return 0
    
    
    def create_file_pull_data(self,robot_id,proto_pull_head):
        Logger().get_logger().info("create_file_pull_data file id:{}, name:{}".format(proto_pull_head.file_id.value, proto_pull_head.file_name.value)) 
        map_file_info = {}
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            print("create_file_pull_data cannot find robot[%d]" % robot_id)
            return ERRNO_FILE_NORMAL
        t_file_info = map_file_info.get(proto_pull_head.file_id.value)
        if t_file_info is None:
            file_mutex.release()
            print("create_file_pull_data file[%d] doesnot exist in list" % proto_pull_head.file_id.value)
            return ERRNO_FILE_NORMAL
        
        t_file_info.m_hd = self.__file_rw.create_file(t_file_info.m_name)
        if -1 == t_file_info.m_hd:
            print("wite file[%s] failure" % t_file_info.m_name)
            file_mutex.release()
            #notify agvshell
            self.notify(userid,robot_id,file_path,t_file_info.m_type,0,ERRNO_FILE_CREATE,-1,taskId)
            self.task_finish(userid,threadID,taskId,t_file_info.m_oper_type)
            return ERRNO_FILE_CREATE
        
        t_file_info.m_size = proto_pull_head.total_size.value
        t_file_info.m_ctime = int(proto_pull_head.file_create_time.value / 10000000 - 11644473600) #11644444800+8*60*60
        t_file_info.m_atime = int(proto_pull_head.file_access_time.value / 10000000 - 11644473600)
        t_file_info.m_mtime = int(proto_pull_head.file_modify_time.value / 10000000 - 11644473600)
        t_file_info.m_last_block_num = 0
        t_file_info.m_last_off = 0
        t_file_info.m_block_size = self.get_block_size()
        t_file_info.m_block_num = int(t_file_info.m_size / t_file_info.m_block_size)
        if t_file_info.m_size % t_file_info.m_block_size > 0:
            t_file_info.m_block_num += 1
        #map_file_info[t_file_info.m_file_id] = t_file_info
        #dict_file_info[robot_id] = map_file_info
        Logger().get_logger().info('pull file head secuss, file size:{0}, block_num: {1}'.format(t_file_info.m_size, t_file_info.m_block_num))
        file_mutex.release()
        
        self.pull_file_data(robot_id,proto_pull_head.file_id.value,0) #begin from 0
        self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,0,0,0,t_file_info.m_task_id,t_file_info.m_size)
        
    
    def send_file_data(self,robot_id,file_id,block_num):
        Logger().get_logger().info('send_file_data file id:{}, block num:{}'.format(file_id, block_num))
        map_file_info = {}
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            Logger().get_logger().error('send_file_data cannot find robot[{}]'.format(robot_id))
            return -1
        
        t_file_info = map_file_info.get(file_id)
        if t_file_info is None:
            #self.print_file_dic_list()
            file_mutex.release()
            Logger().get_logger().error('send_file_data file[{}] doesnot exist in list'.format(file_id))
            return -1
        
        shell_info = self.__shell_manager.get_session_by_id(robot_id)
        if shell_info is None:
            #print("session cannot find, robot_id:%d" % robot_id)
            file_mutex.release()
            # self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,0,ERRNO_ROBOT_CONNECT,-1,t_file_info.m_task_id)
            # self.task_finish(t_file_info.m_user_id,t_file_info.m_thread_uid,t_file_info.m_task_id,t_file_info.m_oper_type)
            #在关闭/断链中处理移除正在传输的文件信息
            # self.remove_file_info(robot_id,file_id)  
            return ERRNO_ROBOT_CONNECT

        if block_num < t_file_info.m_block_num:
            #print("begin send file[%s][%d] data" % (t_file_info.m_name,t_file_info.m_file_id))
            #resize m_block_num
            t_file_info.m_block_num = t_file_info.m_last_block_num + int((t_file_info.m_size - t_file_info.m_last_off) / t_file_info.m_block_size)
            if (t_file_info.m_size - t_file_info.m_last_off) % t_file_info.m_block_size > 0:
                t_file_info.m_block_num += 1
            # print("file bn:%d,last off:%d / bnum:%d" % (t_file_info.m_block_num,t_file_info.m_last_off,t_file_info.m_last_block_num))
            data = self.__file_rw.read_file(t_file_info.m_hd, t_file_info.m_last_off, t_file_info.m_block_size)
                        
            shell_info.push_file_data(t_file_info.m_file_id,block_num,t_file_info.m_last_off,data)

            t_file_info.m_last_block_num += 1
            t_file_info.m_last_off += t_file_info.m_block_size
            t_file_info.m_oper_time = int(round(time.time() * 1000))
            
            #call back step
            step = t_file_info.m_last_block_num * 100 // t_file_info.m_block_num
            t_file_info.m_step,step = step,t_file_info.m_step
            file_mutex.release()
            if step != t_file_info.m_step :
                self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,t_file_info.m_step,0,0,t_file_info.m_task_id,t_file_info.m_size)
        else:
            #finish transform
            Logger().get_logger().info('file[{0}][{1}] data send finish'.format(t_file_info.m_name,t_file_info.m_file_id))
            shell_info.file_complete(t_file_info.m_file_id,block_num,FILE_STATUS_NORMAL)
            t_file_info.m_hd.close()
            if FILE_TYPE_A_UPGRADE == t_file_info.m_type:
                shell_info.set_upgrade(FILE_TYPE_NORMAL)
            #call back step
            self.remove_file_info(robot_id,file_id)
            file_mutex.release()
            self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,100,0,1,t_file_info.m_task_id,t_file_info.m_size)
            self.task_finish(t_file_info.m_user_id,t_file_info.m_thread_uid,t_file_info.m_task_id,t_file_info.m_oper_type)
        pass

    def pull_file_data(self,robot_id,file_id,block_num,off=0,data_len=0,data=""):
        # print("pull_file_data file id:%d, block num:%d" % (file_id, block_num))
        map_file_info = {}
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            Logger().get_logger().error('send_file_data cannot find robot[{}]'.format(robot_id))
            return -1
        t_file_info = map_file_info.get(file_id)
        if t_file_info is None:
            file_mutex.release()
            Logger().get_logger().error('send_file_data file[{}] doesnot exist in list'.format(file_id))
            return -1
        
        if t_file_info.m_hd is not None and data != "":
            ret = self.__file_rw.write_file(t_file_info.m_hd, off, data_len, data)
            print("write file[%s] ret[%d]" % (t_file_info.m_name, ret))
        
        shell_info = self.__shell_manager.get_session_by_id(robot_id)
        if shell_info is None:
            print("session cannot find, robot_id:%d" % robot_id)
            file_mutex.release()
            # self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,0,ERRNO_ROBOT_CONNECT,-1,t_file_info.m_task_id)
            # self.task_finish(t_file_info.m_user_id,t_file_info.m_thread_uid,t_file_info.m_task_id,t_file_info.m_oper_type)
            return ERRNO_ROBOT_CONNECT
        
        if block_num < t_file_info.m_block_num:
            #print("begin pull file[%s][%d] data" % (t_file_info.m_name,t_file_info.m_file_id))
            #resize block_num
            t_file_info.m_block_num = t_file_info.m_last_block_num + int((t_file_info.m_size - t_file_info.m_last_off) / t_file_info.m_block_size)
            if (t_file_info.m_size - t_file_info.m_last_off) % t_file_info.m_block_size > 0:
                t_file_info.m_block_num += 1
            
            read_len = t_file_info.m_block_size
            if 1 == (t_file_info.m_block_num - block_num):
                read_len = t_file_info.m_size - t_file_info.m_last_off #last block
            
            shell_info.pull_file_data(t_file_info.m_file_id,block_num,t_file_info.m_last_off,read_len)
            
            t_file_info.m_last_off += read_len
            t_file_info.m_oper_time = int(round(time.time() * 1000))
            print("begin pull file[%s][%d] data, off[%d], len[%d]" % (t_file_info.m_name,t_file_info.m_file_id,t_file_info.m_last_off,read_len))
            
            #call back step
            step = t_file_info.m_last_block_num * 100 // t_file_info.m_block_num
            t_file_info.m_last_block_num += 1
            t_file_info.m_step,step = step,t_file_info.m_step
            # print(step,t_file_info.m_step)
            file_mutex.release()
            if step != t_file_info.m_step :
                self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,t_file_info.m_step,0,0,t_file_info.m_task_id,t_file_info.m_size)
        else:
            #finish file transform
            Logger().get_logger().info('file[{0}][{1}] data pull finish'.format(t_file_info.m_name,t_file_info.m_file_id))

            shell_info.file_complete(t_file_info.m_file_id,block_num,FILE_STATUS_NORMAL)
            
            t_file_info.m_hd.close()
            self.remove_file_info(robot_id,file_id)

            self.__file_rw.set_file_attr(t_file_info.m_name,t_file_info.m_atime,t_file_info.m_ctime,t_file_info.m_mtime)
            
            #call back step
            file_mutex.release()
            self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,100,0,1,t_file_info.m_task_id,t_file_info.m_size)
            self.task_finish(t_file_info.m_user_id,t_file_info.m_thread_uid,t_file_info.m_task_id,t_file_info.m_oper_type)       
        
    
    
    def file_err(self,robot_id,file_id,error_code):
        print("file_err robot id[%d], file id:%d" % (robot_id, file_id))
        map_file_info = {}
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            print("file_err cannot find robot[%d]" % robot_id)
            return -1
        t_file_info = map_file_info.get(file_id)
        if t_file_info is None:
            file_mutex.release()
            print("file_err file[%d] doesnot exist in list" % file_id)
            return -1
        #关闭句柄
        t_file_info.m_hd.close()
        #传输队列中删除
        self.task_finish(t_file_info.m_user_id,t_file_info.m_thread_uid,t_file_info.m_task_id,t_file_info.m_oper_type)
        
        #全局正在传输的字典中删除对应的文件信息
        self.remove_file_info(robot_id,file_id)
        if t_file_info.m_oper_type == FILE_OPER_TYPE_PULL and os.path.exists(t_file_info.m_name):
            os.remove(t_file_info.m_name)
        file_mutex.release()

        if FILE_TYPE_A_UPGRADE == t_file_info.m_type:  
            if self.__shell_manager is not None:
                shell_info = self.__shell_manager.get_session_by_id(robot_id)
                shell_info.set_upgrade(FILE_TYPE_NORMAL)
            else:
                print("session cannot find, robot_id:%d" % robot_id)
                self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,0,ERRNO_ROBOT_CONNECT,-1,t_file_info.m_task_id,-1)
                return ERRNO_ROBOT_CONNECT
              
        Logger().get_logger().info('file[{0}] transform err:{1}'.format(t_file_info.m_path, error_code))
        #call back step
        step = 0
        if t_file_info.m_block_num != 0:
            step = t_file_info.m_last_block_num * 100 // t_file_info.m_block_num
        self.notify(t_file_info.m_user_id,robot_id,t_file_info.m_path,t_file_info.m_type,step,ERRNO_FILE_TRANIMIT,-1,t_file_info.m_task_id,-1)
        
    def print_file_dic_list(self):
        for k1 in dict_file_info.keys():
            print("print_file_dic_list k1:%d" % k1)
            for (k2,v2) in dict_file_info[k1].items():
                print("print_file_dic_list k2:%d::v2:%s" % (k2, v2.m_path))
        pass
        
    def close_robot_file(self,robot_id):
        map_file_info = {}
        file_mutex.acquire()

        #关闭连接/断链后 关于该车的 所有正在传输的任务进行取消
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is not None:
            for k in list(map_file_info):
                val = map_file_info[k]
                val.m_hd.close()
                #删除失败文件
                if val.m_oper_type == FILE_OPER_TYPE_PULL and os.path.exists(val.m_name):
                    os.remove(val.m_name)
                self.notify(val.m_user_id,robot_id,val.m_path,val.m_type,0,ERRNO_FILE_SESSION_CLOSE,1,val.m_task_id,-1)
                self.task_finish(val.m_user_id,val.m_thread_uid,val.m_task_id,val.m_oper_type)

            del map_file_info
            del (dict_file_info[robot_id])
        file_mutex.release()
        
    
    def cancle_file_transform(self,user_id,robot_id,task_id_list = []):
        #可能还在任务队列中
        remove_list = list()
        try:
            if len(task_id_list) <=0:
                return

            self.__transfer_queue_mutex.acquire()
            transfer_queue = self.__map_user_transfer_queue.get(user_id)
            if transfer_queue :
                #取消待传输文件任务
                del_task = transfer_queue.del_task(len(task_id_list),lambda task:task.m_task_id in task_id_list and task.m_robot_id == robot_id)
                for task_info in del_task:
                    # self.notify(user_id,robot_id,task.m_file_path,task.m_file_type,0,ERRNO_FILE_CANCLE,1,task.m_task_id,-1)
                    task_id_list.remove(task_info.m_task_id)
                    remove_list.append(task_info.m_task_id)

                #取消正在传输的任务
                if len(task_id_list) > 0:
                    file_mutex.acquire()
                    map_file_info = dict_file_info.get(robot_id)
                    if map_file_info is not None:
                        remove_id_list = {file_id:file_info for file_id,file_info in map_file_info.items() if file_info.m_task_id in task_id_list}
                        for key,val in remove_id_list.items():
                            shell_info = self.__shell_manager.get_session_by_id(robot_id)
                            if shell_info is None:
                                print("session cannot find, robot_id:%d" % robot_id)
                                # self.notify(user_id,robot_id,val.m_path,val.m_type,0,ERRNO_ROBOT_CONNECT,-1,task.m_task_id,-1)
                                # self.task_finish(user_id,val.m_thread_uid,val.m_task_id,val.m_oper_type)
                                #断链中处理
                                continue
                            shell_info.file_complete(val.m_file_id,val.m_last_block_num,FILE_STATUS_CANCLE)
                            if FILE_TYPE_A_UPGRADE == val.m_type:
                                shell_info.set_upgrade(FILE_TYPE_NORMAL)         
                            Logger().get_logger().info('cancle file transform:{0}'.format(val.m_path))
                              
                            # self.notify(user_id,robot_id,val.m_path,val.m_type,0,ERRNO_FILE_CANCLE,-1,task.m_task_id,-1)
                            self.task_finish(user_id,val.m_thread_uid,val.m_task_id,val.m_oper_type)
                            remove_list.append(val.m_task_id)
                            map_file_info.pop(key)
                            val.m_hd.close()
                            #取消任务，删除文件
                            if val.m_oper_type == FILE_OPER_TYPE_PULL and os.path.exists(val.m_name):
                                os.remove(val.m_name)
                    file_mutex.release()
            self.__transfer_queue_mutex.release()
            return remove_list
        except Exception as e:
            Logger().get_logger().error('cancle file transform error:{0}'.format(val.m_path))
            return remove_list
        
    '''
    file_manager interface begin
    '''
    def push_file_task(self,user_id,robot_list,file_path,file_type,package_id) ->(list,list):
        '''
        push 'push file task to task pool'
        '''
        task_list = []
        err_list = []
        self.__transfer_queue_mutex.acquire()
        transform_queue = self.__map_user_transfer_queue.get(user_id)
        if transform_queue is not None:
            task_list,err_list = transform_queue.push_file_task(user_id,robot_list,file_path,file_type,package_id)
        else:
            transform_queue = user_transfer_queue(self.assign_task_id)
            task_list,err_list = transform_queue.push_file_task(user_id,robot_list,file_path,file_type,package_id)
            self.__map_user_transfer_queue[user_id] = transform_queue
        self.__transfer_queue_mutex.release()

        return task_list,err_list
        
        
    def pull_file_task(self,user_id,file_type,route_path_list):
        '''
        push 'pull file task to task pool'
        '''
        task_list = []
        err_list = []
        self.__transfer_queue_mutex.acquire()
        transform_queue = self.__map_user_transfer_queue.get(user_id)
        if transform_queue is not None:
            task_list,err_list = transform_queue.pull_file_task(user_id,file_type,route_path_list)
        else:
            transform_queue = user_transfer_queue(self.assign_task_id)
            task_list,err_list = transform_queue.pull_file_task(user_id,file_type,route_path_list)
            self.__map_user_transfer_queue[user_id] = transform_queue
        self.__transfer_queue_mutex.release()

        return task_list,err_list
        
    def change_file_dir(self,dic):
        '''
        change pull files storage directory
        '''
        if dic != "":
            self.__file_dir = str(dic)
            Logger().get_logger().info('default dir change to:{0}'.format(self.__file_dir))

            
    def change_block_size(self,size):
        '''
        change each block size, support dynamic tuning
        '''
        if size is not None and 0 != size:
            self.__block_size = int(size)
            Logger().get_logger().info('file transform size change to:{0}'.format(self.__block_size))

    def register_notify_changed(self,notify_callback = None):
        self.__notify_callback = notify_callback

        
    def register_shell_manager(self,sh_mn = None):
        self.__shell_manager = sh_mn

    
    def check_file_timeout(self,now_t):
        CHECK_FILE_TRANSFORM_OUT = 10000  #default timeout 10s 
        file_mutex.acquire()
        try:
            for k1 in list(dict_file_info):
                v1 = dict_file_info[k1]
                print("robot_id:val ::", k1, v1)
                for k2 in list(v1):
                    print("key:%d, val file name:%s" % (k2, v1[k2].m_name))
                    diff_time = now_t - v1[k2].m_oper_time
                    if diff_time > CHECK_FILE_TRANSFORM_OUT:
                        Logger().get_logger().info('file name[{0}] transform timeout:{1}.'.format(v1[k2].m_name, diff_time))
                        if v1[k2].m_hd is not None and -1 != v1[k2].m_hd:
                            v1[k2].m_hd.close()
                        if FILE_OPER_TYPE_PULL == v1[k2].m_oper_type:
                            t_size,t_ctime,t_atime,t_mtime = self.__file_rw.get_file_attr(v1[k2].m_name)
                            if t_size != v1[k2].m_size:
                                shutil.rmtree(v1[k2].m_name)
                                Logger().get_logger().info('file[{0}] timeout and unfinish transform, delete it.'.format(v1[k2].m_name))
                        
                        if self.__shell_manager is not None:
                            shell_info = self.__shell_manager.get_session_by_id(k1)
                            if shell_info is not None:
                                print("file id,block_num", v1[k2].m_file_id,v1[k2].m_last_block_num)
                                shell_info.file_complete(v1[k2].m_file_id,v1[k2].m_last_block_num,FILE_STATUS_TIMEOUT)
                                if FILE_TYPE_A_UPGRADE == v1[k2].m_type:
                                    shell_info.set_upgrade(FILE_TYPE_NORMAL)

                        self.notify(v1[k2].m_user_id,[k1],v1[k2].m_path,v1[k2].m_type,0,ERRNO_FILE_TIMEOUT,v1[k2].m_task_id,-1)
                        self.task_finish(v1[k2].m_user_id,v1[k2].m_thread_uid,v1[k2].m_task_id,v1[k2].m_oper_type)
                        v1.pop(k2)
                if len(dict_file_info[k1]) <= 0:
                    dict_file_info.pop(k1)
        except Exception as e:
            print("timeout exception:", e)
        file_mutex.release()
    pass

    
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)
