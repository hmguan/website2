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

#文件类型 
FILE_TYPE_NORMAL=0
FILE_TYPE_A_UPGRADE=0x0001
FILE_TYPE_VCU_UPGRADE=0x0010

#file_status
FILE_STATUS_TIMEOUT = -5
FILE_STATUS_CANCLE = -4
FILE_STATUS_UNINIT = -3
FILE_STATUS_READ_ERROR = -2
FILE_STATUS_WRITE_ERROR = -1
FILE_STATUS_NORMAL = 0
FILE_STATUS_COMPLETE = 1

#file operator type
FILE_OPER_TYPE_PUSH = 1
FILE_OPER_TYPE_PULL = 2

#文件传输并发数 
MAX_THREAD_NUM = 1
#最大任务数 
MAX_QUEUE_NUM = 1000

#<key:robot_id, value:<file_id, file_info> >
dict_file_info={}
#全局数据锁  
file_mutex=threading.RLock()
#dict for upgrade
dict_robot_upgrade={} 


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
        self.__work_queue = queue.Queue(MAX_QUEUE_NUM)
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
        self.m_work_queue.clear()
        self.__queue_mutex.release()
        
    def init_pool(self):
        if len(self.__work_threads) > 0:
            return -1
            
        for i in range(MAX_THREAD_NUM):
            print(i)
            t_th = threading.Thread(target=task_thread_pool.th_handler,args=(self,i,))
            t_th.setDaemon(True)
            t_th.start()
            self.__work_threads.append(t_th)
            pass
    
    def th_handler(self,id):
        thread_id = id
        self.__is_working[thread_id] = False
        print("thread id:%d" % thread_id)
        while 0 == self.__exit_flag:
            if self.__is_working[thread_id]:
                time.sleep(2)
                continue
            self.__queue_mutex.acquire()
            while self.__work_queue.empty():
                self.__queue_mutex.release()
                print("thread:%d waiting" % thread_id)
                self.__thread_wait.wait()
                self.__thread_wait.reset()
                print("thread:%d wake up" % thread_id)
                if self.__exit_flag > 0:
                    return
                self.__queue_mutex.acquire()
                
            
            task = self.__work_queue.get_nowait()
            print("thread:%d start task, queue size:%d" % (thread_id, self.__work_queue.qsize()))
            self.__is_working[thread_id] = True
            self.__queue_mutex.release()
            ret = task.on_task(thread_id)
            print("thread:%d after on_task ret:%d" % (thread_id, ret))
            if ret != 0:
                self.__is_working[thread_id] = False
            
        print("thread id:%d exit" % thread_id)
        
    def add_task(self,task):
        self.__queue_mutex.acquire()
        if self.__work_queue.full():
            print("task queue full!!!")
            return -1
        self.__work_queue.put_nowait(task)
        self.__queue_mutex.release()
        self.__thread_wait.sig()
        pass
        
    def del_task(self,session_uid,robot_id,file_path):
        '''
        specile for file_task
        '''
        self.__queue_mutex.acquire()
        for task in self.__work_queue:
            if session_uid == task.m_session_uid and robot_id == task.m_robot_id and file_path == task.m_file_path:
                task.m_oper_type = 0
                return task.m_file_type
        self.__queue_mutex.release()
        return -1
    
    def task_finish(self,thread_id):
        self.__is_working[thread_id] = False
        print("thread[%d] working status change" % thread_id)
        pass
    
    def thread_join(self):
        self.__thread_wait.sig()
        for th in self.__work_threads:
            th.join()
        pass


class agvfile():
    def __init__(self):
        
        pass

    def __del__(self):
        pass

    def create_file(self,name):
        try:
            fd = open(name, 'wb')
        except IOError:
            print ('create_file file %s failure' % name)
            return -1
        else:
            print ('create_file file %s success' % name)
            return fd

    def open_file(self,name):
        try:
            fd=open(name, 'rb')
        except IOError:
            print ('open_file %s failure' % name)
            return -1
        else:
            print ('open_file %s success' % name)
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
    def __init__(self,s_uid,r_id,f_path,f_type,oper_type):
        self.m_session_uid = s_uid
        self.m_robot_id = r_id
        self.m_file_path = f_path
        self.m_file_type = f_type
        self.m_oper_type = oper_type
    
    def on_task(self,thread_id):
        ret = -1
        if FILE_OPER_TYPE_PUSH == self.m_oper_type:
            ret = file_manager().push_file(thread_id,self.m_session_uid,self.m_robot_id,self.m_file_path,self.m_file_type)
        elif FILE_OPER_TYPE_PULL == self.m_oper_type:
            ret = file_manager().pull_file(thread_id,self.m_session_uid,self.m_robot_id,self.m_file_path)
        else:
            print("for delete task")
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

    def __del__(self):
        if self.m_hd is not None and -1 != self.m_hd:
            self.m_hd.close()
    

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
        self.__task_thread_pool = task_thread_pool()

    def __del__(self):
        del self.__task_thread_pool
        pass

    def allocate_file_id(self):
        self.__file_id_mutex.acquire()
        self.__file_id += 1
        self.__file_id_mutex.release()
        return self.__file_id
    
    def push_file(self,threadID,session_uid,robot_id,file_path,file_type):
        if self.__shell_manager is None:
            print("shell manager regist failure, robot_id:%d" % robot_id)
            if self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,file_type,0,ERRNO_ROBOT_CONNECT,-1)
            self.__task_thread_pool.task_finish(threadID)
            return ERRNO_ROBOT_CONNECT
        
        shell_info = self.__shell_manager.get_session_by_id(robot_id)
        if shell_info is None:
            print("session cannot find, robot_id:%d" % robot_id)
            if self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,file_type,0,ERRNO_ROBOT_CONNECT,-1)
            self.__task_thread_pool.task_finish(threadID)
            return ERRNO_ROBOT_CONNECT
        
        t_file_info = file_info()
        t_file_info.m_hd = self.__file_rw.open_file(file_path)
        if -1 == t_file_info.m_hd:
            print("open file[%s] failure" % file_path)
            if self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,file_type,0,ERRNO_FILE_OPEN,-1)
            self.__task_thread_pool.task_finish(threadID)
            return ERRNO_FILE_OPEN
        
        t_file_info.m_type = file_type
        if FILE_TYPE_A_UPGRADE == t_file_info.m_type:
            if FILE_TYPE_A_UPGRADE == shell_info.get_upgrade_flag():
                print("upgrade exit, stop this time upgrade")
                if self.__notify_callback is not None:
                    self.__notify_callback(session_uid,robot_id,file_path,file_type,0,ERRNO_FILE_UPGRADE,-1)
                self.__task_thread_pool.task_finish(threadID)
                if robot_id in dict_robot_upgrade.keys():
                    del dict_robot_upgrade[robot_id]
                return ERRNO_FILE_UPGRADE
            shell_info.set_upgrade(FILE_TYPE_A_UPGRADE)
        
        t_file_info.m_path = file_path
        t_file_info.m_name = file_path[file_path.rfind('/') + 1:]
        t_file_info.m_file_id = self.allocate_file_id()
        t_file_info.m_size,t_file_info.m_ctime,t_file_info.m_atime,t_file_info.m_mtime = self.__file_rw.get_file_attr(file_path)
        
        shell_info.push_file_head(t_file_info.m_file_id,t_file_info.m_type,t_file_info.m_name,t_file_info.m_size, \
                (t_file_info.m_ctime+11644473600)*10000000,(t_file_info.m_atime+11644473600)*10000000,(t_file_info.m_mtime+11644473600)*10000000)
        t_file_info.m_oper_time = int(round(time.time() * 1000))
        t_file_info.m_oper_type = FILE_OPER_TYPE_PUSH
        t_file_info.m_session_uid = session_uid
        t_file_info.m_thread_uid = threadID
        t_file_info.m_last_block_num = 0
        t_file_info.m_last_off = 0
        t_file_info.m_block_num = int(t_file_info.m_size / self.__block_size)
        if t_file_info.m_size % self.__block_size > 0:
            t_file_info.m_block_num += 1
        
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            map_file_info = {}
            map_file_info[t_file_info.m_file_id] = t_file_info
            dict_file_info[robot_id] = map_file_info
        else:
            map_file_info[t_file_info.m_file_id] = t_file_info
        #self.print_file_dic_list()
        file_mutex.release()
        
        Logger().get_logger().info('push file head secuss, name:{0} size:{1}, block_num: {2}'.format(t_file_info.m_path, t_file_info.m_size, t_file_info.m_block_num))
        return 0
    
    
    def pull_file(self,threadID,session_uid,robot_id,file_path):
        if file_path == "":
            if self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,FILE_TYPE_NORMAL,0,ERRNO_FILE_OPEN,-1)
            self.__task_thread_pool.task_finish(threadID)
            return ERRNO_FILE_OPEN
        
        if self.__shell_manager is None:
            print("shell manager regist failure, robot_id:%d" % robot_id)
            if self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,FILE_TYPE_NORMAL,0,ERRNO_ROBOT_CONNECT,-1)
            self.__task_thread_pool.task_finish(threadID)
            return ERRNO_ROBOT_CONNECT
        
        shell_info = self.__shell_manager.get_session_by_id(robot_id)
        if shell_info is None:
            print("session cannot find, robot_id:%d" % robot_id)
            if self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,FILE_TYPE_NORMAL,0,ERRNO_ROBOT_CONNECT,-1)
            self.__task_thread_pool.task_finish(threadID)
            return ERRNO_ROBOT_CONNECT
        
        t_file_info = file_info()
        t_file_info.m_name = self.__file_dir + file_path[file_path.rfind('/') + 1:]
        t_file_info.m_path = file_path
        t_file_info.m_file_id = self.allocate_file_id()
        
        shell_info.pull_file_head(t_file_info.m_file_id,file_path)
        
        t_file_info.m_oper_time = int(round(time.time() * 1000))
        t_file_info.m_oper_type = FILE_OPER_TYPE_PULL
        t_file_info.m_session_uid = session_uid
        t_file_info.m_thread_uid = threadID
        
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            map_file_info = {}
            map_file_info[t_file_info.m_file_id] = t_file_info
            dict_file_info[robot_id] = map_file_info
        else:
            map_file_info[t_file_info.m_file_id] = t_file_info
        #self.print_file_dic_list()
        file_mutex.release()
        
        Logger().get_logger().info('begin to pull file:{0}, file id:{1}'.format(t_file_info.m_name, t_file_info.m_file_id))
        return 0
    
    
    def create_file_pull_data(self,robot_id,proto_pull_head):
        print("create_file_pull_data file id:%d, name:%s" % (proto_pull_head.file_id.value, proto_pull_head.file_name.value))
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
            file_mutex.release()
            print("wite file[%s] failure" % t_file_info.m_name)
            #notify agvshell
            if self.__notify_callback is not None:
                self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,FILE_TYPE_NORMAL,0,ERRNO_FILE_CREATE,-1)
            self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
            return ERRNO_FILE_CREATE
        
        t_file_info.m_size = proto_pull_head.total_size.value
        t_file_info.m_ctime = int(proto_pull_head.file_create_time.value / 10000000 - 11644473600) #11644444800+8*60*60
        t_file_info.m_atime = int(proto_pull_head.file_access_time.value / 10000000 - 11644473600)
        t_file_info.m_mtime = int(proto_pull_head.file_modify_time.value / 10000000 - 11644473600)
        print("file:%s, get attr:%d,%d,%d" % (t_file_info.m_name,t_file_info.m_atime,t_file_info.m_ctime,t_file_info.m_mtime))
        t_file_info.m_last_block_num = 0
        t_file_info.m_last_off = 0
        t_file_info.m_block_num = int(t_file_info.m_size / self.__block_size)
        if t_file_info.m_size % self.__block_size > 0:
            t_file_info.m_block_num += 1
        #map_file_info[t_file_info.m_file_id] = t_file_info
        #dict_file_info[robot_id] = map_file_info
        Logger().get_logger().info('pull file head secuss, file size:{0}, block_num: {1}'.format(t_file_info.m_size, t_file_info.m_block_num))
        file_mutex.release()
        
        self.pull_file_data(robot_id,proto_pull_head.file_id.value,0) #begin from 0 
        
    
    def send_file_data(self,robot_id,file_id,block_num):
        #print("send_file_data file id:%d, block num:%d" % (file_id, block_num))
        map_file_info = {}
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            print("send_file_data cannot find robot[%d]" % robot_id)
            return -1
        
        t_file_info = map_file_info.get(file_id)
        if t_file_info is None:
            #self.print_file_dic_list()
            file_mutex.release()
            print("send_file_data file[%d] doesnot exist in list" % file_id)
            return -1
        
        if block_num < t_file_info.m_block_num:
            #print("begin send file[%s][%d] data" % (t_file_info.m_name,t_file_info.m_file_id))
            #resize m_block_num
            t_file_info.m_block_num = t_file_info.m_last_block_num + int((t_file_info.m_size - t_file_info.m_last_off) / self.__block_size)
            if (t_file_info.m_size - t_file_info.m_last_off) % self.__block_size > 0:
                t_file_info.m_block_num += 1
            # print("file bn:%d,last off:%d / bnum:%d" % (t_file_info.m_block_num,t_file_info.m_last_off,t_file_info.m_last_block_num))
            data = self.__file_rw.read_file(t_file_info.m_hd, t_file_info.m_last_off, self.__block_size)
            
            shell_info = self.__shell_manager.get_session_by_id(robot_id)
            if shell_info is None:
                #print("session cannot find, robot_id:%d" % robot_id)
                if self.__notify_callback is not None:
                    self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,t_file_info.m_type,0,ERRNO_ROBOT_CONNECT,-1)
                self.__task_thread_pool.task_finish(threadID)
                file_mutex.release()
                return ERRNO_ROBOT_CONNECT
            
            shell_info.push_file_data(t_file_info.m_file_id,block_num,t_file_info.m_last_off,data)
            
            t_file_info.m_last_block_num += 1
            t_file_info.m_last_off += self.__block_size
            t_file_info.m_oper_time = int(round(time.time() * 1000))
            
            #call back step
            if self.__notify_callback is not None:
                step = format(t_file_info.m_last_block_num / t_file_info.m_block_num * 100, '.2f')
                self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,t_file_info.m_type,step,0,0)
        else:
            #finish transform
            Logger().get_logger().info('file[{0}][{1}] data send finish'.format(t_file_info.m_name,t_file_info.m_file_id))
            
            shell_info = self.__shell_manager.get_session_by_id(robot_id)
            if shell_info is None:
                print("session cannot find, robot_id:%d" % robot_id)
                if self.__notify_callback is not None:
                    self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,t_file_info.m_type,0,ERRNO_ROBOT_CONNECT,-1)
                file_mutex.release()
                self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
                return ERRNO_ROBOT_CONNECT
            shell_info.file_complete(t_file_info.m_file_id,block_num,FILE_STATUS_NORMAL)
            if robot_id in dict_robot_upgrade.keys():
                del dict_robot_upgrade[robot_id]
            if FILE_TYPE_A_UPGRADE == t_file_info.m_type:
                shell_info.set_upgrade(FILE_TYPE_NORMAL)
            
            #call back step
            if self.__notify_callback is not None:
                self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,t_file_info.m_type,100,0,1,t_file_info.m_size)
            
            self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
            del (map_file_info[file_id])
            if 0 == len(dict_file_info[robot_id]):
                del (dict_file_info[robot_id])
                
            
        file_mutex.release()
        pass
    
    
    def pull_file_data(self,robot_id,file_id,block_num,off=0,data_len=0,data=""):
        print("pull_file_data file id:%d, block num:%d" % (file_id, block_num))
        map_file_info = {}
        file_mutex.acquire()
        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            print("pull_file_data cannot find robot[%d]" % robot_id)
            return -1
        t_file_info = map_file_info.get(file_id)
        if t_file_info is None:
            file_mutex.release()
            print("pull_file_data file[%d] doesnot exist in list" % file_id)
            return -1
        
        if t_file_info.m_hd is not None and data != "":
            ret = self.__file_rw.write_file(t_file_info.m_hd, off, data_len, data)
            print("write file[%s] ret[%d]" % (t_file_info.m_name, ret))
        
        if block_num < t_file_info.m_block_num:
            #print("begin pull file[%s][%d] data" % (t_file_info.m_name,t_file_info.m_file_id))
            #resize block_num
            t_file_info.m_block_num = t_file_info.m_last_block_num + int((t_file_info.m_size - t_file_info.m_last_off) / self.__block_size)
            if (t_file_info.m_size - t_file_info.m_last_off) % self.__block_size > 0:
                t_file_info.m_block_num += 1
            
            read_len = self.__block_size
            if 1 == (t_file_info.m_block_num - block_num):
                read_len = t_file_info.m_size - t_file_info.m_last_off #last block
            
            shell_info = self.__shell_manager.get_session_by_id(robot_id)
            if shell_info is None:
                print("session cannot find, robot_id:%d" % robot_id)
                if self.__notify_callback is not None:
                    self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,FILE_TYPE_NORMAL,0,ERRNO_ROBOT_CONNECT,-1)
                file_mutex.release()
                self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
                return ERRNO_ROBOT_CONNECT
            shell_info.pull_file_data(t_file_info.m_file_id,block_num,t_file_info.m_last_off,read_len)
            
            t_file_info.m_last_block_num += 1
            t_file_info.m_last_off += read_len
            t_file_info.m_oper_time = int(round(time.time() * 1000))
            print("begin pull file[%s][%d] data, off[%d], len[%d]" % (t_file_info.m_name,t_file_info.m_file_id,t_file_info.m_last_off,read_len))
            
            #call back step
            if self.__notify_callback is not None:
                step = format(t_file_info.m_last_block_num / t_file_info.m_block_num * 100, '.2f')
                self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,FILE_TYPE_NORMAL, step, 0, 0)
        else:
            #finish file transform
            Logger().get_logger().info('file[{0}][{1}] data pull finish'.format(t_file_info.m_name,t_file_info.m_file_id))
            shell_info = self.__shell_manager.get_session_by_id(robot_id)
            if shell_info is None:
                print("session cannot find, robot_id:%d" % robot_id)
                if self.__notify_callback is not None:
                    self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,FILE_TYPE_NORMAL,0,ERRNO_ROBOT_CONNECT,-1)
                file_mutex.release()
                self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
                return ERRNO_ROBOT_CONNECT
            shell_info.file_complete(t_file_info.m_file_id,block_num,FILE_STATUS_NORMAL)
            
            t_file_info.m_hd.close()
            self.__file_rw.set_file_attr(t_file_info.m_name,t_file_info.m_atime,t_file_info.m_ctime,t_file_info.m_mtime)
            
            #call back step
            if self.__notify_callback is not None:
                self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,FILE_TYPE_NORMAL,100,0,1)
            
            self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
            del (map_file_info[file_id])
            if 0 == len(dict_file_info[robot_id]):
                del (dict_file_info[robot_id])
        file_mutex.release()
    
    
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
        if FILE_TYPE_A_UPGRADE == t_file_info.m_type:
            if robot_id in dict_robot_upgrade.keys():
                del dict_robot_upgrade[robot_id]
            if self.__shell_manager is not None:
                shell_info = self.__shell_manager.get_session_by_id(robot_id)
                shell_info.set_upgrade(FILE_TYPE_NORMAL)
            else:
                print("session cannot find, robot_id:%d" % robot_id)
                if self.__notify_callback is not None:
                    self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,t_file_info.m_type,0,ERRNO_ROBOT_CONNECT,-1)
                file_mutex.release()
                self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
                return ERRNO_ROBOT_CONNECT
            
        
        Logger().get_logger().info('file[{0}] transform err:{1}'.format(t_file_info.m_path, error_code))
        #call back step
        if self.__notify_callback is not None:
            step = 0
            if t_file_info.m_block_num != 0:
                step = format(t_file_info.m_last_block_num / t_file_info.m_block_num * 100, '.2f')
            self.__notify_callback(t_file_info.m_session_uid,robot_id,t_file_info.m_path,t_file_info.m_type,step,error_code,-1)
        
        self.__task_thread_pool.task_finish(t_file_info.m_thread_uid)
        del (map_file_info[file_id])
        if 0 == len(dict_file_info[robot_id]):
            del (dict_file_info[robot_id])
        file_mutex.release()
        
    def print_file_dic_list(self):
        for k1 in dict_file_info.keys():
            print("print_file_dic_list k1:%d" % k1)
            for (k2,v2) in dict_file_info[k1].items():
                print("print_file_dic_list k2:%d::v2:%s" % (k2, v2.m_path))
        pass
        
    def close_robot_file(self,robot_id):
        map_file_info = {}
        file_mutex.acquire()
        if robot_id in dict_robot_upgrade.keys():
            dict_robot_upgrade.pop(robot_id)
        if robot_id not in dict_file_info.keys():
            print('-------can not find robot id in dict file info------')
            file_mutex.release()
            return -1

        map_file_info = dict_file_info.get(robot_id)
        if map_file_info is None:
            file_mutex.release()
            return -1
        
        print("robot:%d closed" % robot_id)

        for k in list(map_file_info):
            val = map_file_info[k]
            if self.__notify_callback is not None:
                self.__notify_callback(val.m_session_uid,robot_id,val.m_path,val.m_type,0,ERRNO_FILE_SESSION_CLOSE,-1)
            self.__task_thread_pool.task_finish(val.m_thread_uid)
            map_file_info.pop(k)
        
        del (dict_file_info[robot_id])
        file_mutex.release()
        
    
    def cancle_file_transform(self,session_uid,robot_id,file_path):
        #可能还在任务队列中 
        try:
            ret = self.__task_thread_pool.del_task(session_uid,robot_id,file_path)
            if ret >= 0 and self.__notify_callback is not None:
                self.__notify_callback(session_uid,robot_id,file_path,ret,0,ERRNO_FILE_CANCLE,-1)
                return
            
            print("cancle task robot id[%d], file id:%d" % (robot_id, file_name))
            map_file_info = {}
            file_mutex.acquire()
            map_file_info = dict_file_info.get(robot_id)
            if map_file_info is None:
                file_mutex.release()
                print("cancle task cannot find robot[%d]" % robot_id)
                return -1
            
            for k in list(map_file_info):
                val = map_file_info[k]
                print("key:%d, val file name:%s" % (k, val.m_path))
                if session_uid == val.m_session_uid and file_path == val.m_path:
                    

                    shell_info = self.__shell_manager.get_session_by_id(robot_id)
                    if shell_info is None:
                        print("session cannot find, robot_id:%d" % robot_id)
                        if self.__notify_callback is not None:
                            self.__notify_callback(session_uid,robot_id,file_path,val.m_type,0,ERRNO_ROBOT_CONNECT,-1)
                        file_mutex.release()
                        self.__task_thread_pool.task_finish(val.m_thread_uid)
                        return ERRNO_ROBOT_CONNECT
                    shell_info.file_complete(val.m_file_id,val.m_last_block_num,FILE_STATUS_CANCLE)
                    if FILE_TYPE_A_UPGRADE == val.m_type:
                        shell_info.set_upgrade(FILE_TYPE_NORMAL)
                        if robot_id in dict_robot_upgrade.keys():
                            dict_robot_upgrade.pop(robot_id)

                    Logger().get_logger().info('cancle file transform:{0}'.format(val.m_path))
                    
                    if self.__notify_callback is not None:
                        self.__notify_callback(val.m_session_uid,robot_id,file_path,val.m_type,0,ERRNO_FILE_CANCLE,-1)
                    self.__task_thread_pool.task_finish(val.m_thread_uid)
                    map_file_info.pop(k)
                    break
            
            file_mutex.release()
        except Exception as e:
            print("cancle exception:", e)
            
        
        
    '''
    file_manager interface begin
    '''
    def push_file_task(self,session_uid,robot_list,file_path,file_type):
        '''
        push 'push file task to task pool'
        '''
        for item in robot_list:
            robot_id = int(item)
            global dict_robot_upgrade
            print("push_file_task file:,robot id:,robot upgrade:", file_path, robot_id, dict_robot_upgrade)
            if FILE_TYPE_A_UPGRADE == file_type and robot_id in dict_robot_upgrade.keys():
                if self.__notify_callback is not None:
                    self.__notify_callback(session_uid,robot_id,file_path,file_type,0,ERRNO_FILE_UPGRADE,-1)
                print("exist upgrade package in task list")
                return -1
            dict_robot_upgrade[robot_id] = FILE_TYPE_A_UPGRADE
            task = file_task(session_uid,robot_id,file_path,file_type,FILE_OPER_TYPE_PUSH)
            self.__task_thread_pool.add_task(task)

        return 0
        
        
    def pull_file_task(self,session_uid,robot_list,file_path,file_type=0):
        '''
        push 'pull file task to task pool'
        '''
        for item in robot_list:
            task = file_task(session_uid,int(item),file_path,FILE_TYPE_NORMAL,FILE_OPER_TYPE_PULL)
            self.__task_thread_pool.add_task(task)
        pass
        
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
                                    if k1 in dict_robot_upgrade.keys():
                                        del dict_robot_upgrade[k1]
                                    shell_info.set_upgrade(FILE_TYPE_NORMAL)
                        
                        if self.__notify_callback is not None:
                            self.__notify_callback(v1[k2].m_session_uid,k1,v1[k2].m_path,v1[k2].m_type,0,ERRNO_FILE_TIMEOUT,-1)
                        self.__task_thread_pool.task_finish(v1[k2].m_thread_uid)
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


