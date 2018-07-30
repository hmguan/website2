# -*- coding: utf-8 -*-

from pynsp import obtcp as tcp
from .shproto import proto_head as head,proto_typedef as typedef,login,proto_file,proto_upgrade,proto_sysinfo as sysinfo,proto_log as log
from .shproto import proto_common,proto_process_list
from agvshell import net_manager as nm
from pynsp.encrypt import *
import random
import hashlib
import threading
import time
import copy
import errtypes
from pynsp.logger import *
from pynsp.waite_handler import *
from copy import deepcopy

DAY_SECONDS=86400
HOUR_SECONDS=3600
MIN_SECONDS=60
path_notify_callback=None

class shell_session(tcp.obtcp):
    def __init__(self,rlink = -1,notify_closed=None,notify_file_manager=None,push_notify= None):
        super(shell_session, self).__init__(rlink)
        self.__net_manager=nm.net_manager()
        self.__net_status=typedef.NetworkStatus_Closed
        self.__publickey=bytes()
        self.__robot_id=-1
        self.__target_host=""
        self.__mutex = threading.RLock()
        self.__timestamp = int(round(time.time() * 1000))
        self.__connected_timestamp=int(time.time())
        self.__notify_closed = notify_closed
        self.__notify_fm = notify_file_manager
        #存放agvshell上报的系统配置信息
        self.__shell_systeminfo = {}
        #存放agvshell上报的cpu，memroy信息
        self.__shell_serviceinfo = {}
        #存放agvshell管理的进程的cpu，memory等信息
        self.__shell_process_info= []
        self.__upgrading = 0
        self.__current_netio_r = 0.0
        self.__current_netio_t = 0.0
        self.__log_type=b''
        self.__previous_timestamp = int(round(time.time() * 1000))
        self.__push_notify_cb = push_notify
        return

    def __del__(self):
        Logger().get_logger().info("shell_session del, robot_id:%d" % self.__robot_id)
        super(shell_session,self).__del__()

        return

    def on_accepted(self, rlink):
        Logger().get_logger().info("accept client session")
        client_link = shell_session(rlink)

    def on_recvdata(self, data, cb):
        # for i in range(cb):
        #     print(data[i],end=' ')
        # print('')

        phead = head.proto_head()
        phead.build(data, 0)
        # print('recv packet,type=0x%x'%phead.type)
        pkt_id = phead.id.value

        self.__mutex.acquire()
        self.__timestamp = int(round(time.time() * 1000))
        self.__mutex.release()

        if  typedef.PKTTYPE_AGV_SHELL_PRE_LOGIN_ACK == phead.type:
            self.recv_pre_login(data)
        elif typedef.PKTTYPE_AGV_SHELL_KEEPALIVE_ACK == phead.type:
            self.recv_keepalive_pkt(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_LOGIN_ACK == phead.type:
            Logger().get_logger().info("get agvshell login ack type")
            login_ack = head.proto_head()
            login_ack.build(data, 0)
            if login_ack.err == 0:
                Logger().get_logger().info('login successful.')
                self.__net_status = typedef.NetworkStatus_Established
            else:
                Logger().get_logger().error('login failed.')
        elif typedef.PKTTYPE_AGV_SHELL_GET_FIXED_SYSINFO_ACK== phead.type:
            self.recv_fixed_systeminfo(pkt_id,data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_READ_FILE_HEAD_ACK == phead.type:
            self.recv_pull_file_head(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_PUSH_FILE_HEAD_ACK == phead.type:
            self.recv_push_file_head(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_READ_FILE_BLOCK_ACK == phead.type:
            self.recv_pull_file_data(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_PUSH_FILE_BLOCK_ACK == phead.type:
            self.recv_push_file_data_reply(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_RW_FILE_STATUS_ACK == phead.type:
            self.recv_file_status(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_GET_LOG_TYPE_ACK == phead.type:
            self.recv_log_type(pkt_id, data)
        elif typedef.PKTTYPE_AGV_SHELL_GET_LOG_FILE_NAME_ACK == phead.type:
            self.recv_log_name(data)
        elif typedef.PKTTYPE_AGV_SHELL_FILE_MUTEX_STATUS_ACK == phead.type:
            pass
        elif typedef.PKTTYPE_AGV_SHELL_MODIFY_FILE_MUTEX_ACK == phead.type:
            self.recv_modify_file_mutex(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_UPDATE_NTP_ACK == phead.type:
            self.on_update_ntp_server(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_PROCESS_COMMAND_ACK == phead.type:
            self.on_recv_process_cmd_ack(data,cb)
        elif typedef.PKTTYPE_AGV_SHELL_SET_PROCESS_LIST_ACK:
            self.on_recv_update_process_list_ack(data,cb)
        else:
            Logger().get_logger().warning("not support type:%8x" % phead.type)

    def on_pre_close(self):
        pass

    def on_closed(self, previous):
        self.__net_status=typedef.NetworkStatus_Closed
        if previous >= 0:
            Logger().get_logger().warning("close the session {0} ,lnk is {1}".format(self.__target_host,previous))
            if self.__notify_fm is not None:
                self.__notify_fm.close_robot_file(self.__robot_id)
            if self.__notify_closed is not None:
                Logger().get_logger().warning('notify closed,robot id:{0}'.format(self.__robot_id))
                self.__notify_closed(self.__robot_id)
            global path_notify_callback
            if path_notify_callback is not None:
                path_notify_callback(self.__robot_id, -1, '')
        pass

    def on_connected(self):
        Logger().get_logger().info("success connect to {0}:{1}".format(self.rhost,self.rport))
        pass

    def try_connect(self,ipv4,port,robot_id):
        if self.__net_status == typedef.NetworkStatus_Closed:
            self.__net_status=typedef.NetworkStatus_Actived
            if self.create() < 0:
                return -1
        if self.__net_status == typedef.NetworkStatus_Actived:
            self.__net_status=typedef.NetworkStatus_Connecting
            if self.connect(ipv4,port) < 0:
                self.close()
                Logger().get_logger().error("failed to connect to endpoint:{0}".format(ipv4))
                return -1
            self.__target_host = ipv4
            self.__robot_id=robot_id
        return 0

    def try_login(self):
        self.__net_status = typedef.NetworkStatus_Connected
        login_ack = login.proto_login()

        req = bytearray(32)
        for i in range(32):
            req[i] = random.randint(0, 254) & 0xFF
        login_ack.ori(req)

        out, outcb = encrypt(req, self.__publickey)
        enc = bytearray(outcb)
        for i in range(outcb):
            enc[i] = out[i]
        al = hashlib.md5()
        al.update(enc)
        login_ack.enc(al.digest())

        login_ack.phead.size(login_ack.length())
        stream = login_ack.serialize()
        return self.send(stream, login_ack.length())

    def recv_pre_login(self,data):
        if self.__net_status == typedef.NetworkStatus_Closed:
            Logger().get_logger().warning('current session of target:{0} is closed'.format(self.__target_host))
            return

        pre_login = login.proto_pre_login()
        pre_login.build(data, 0)
        Logger().get_logger().info("get agvshell pre login")
        self.__net_status = typedef.NetworkStatus_Ready
        self.__publickey = pre_login.publickey.value

    def post_alive_pkt(self):
        if self.__net_status == typedef.NetworkStatus_Closed:
            Logger().get_logger().warning('current session of target:{0} is closed'.format(self.__target_host))
            return

        if self.__net_status != typedef.NetworkStatus_Established:
            Logger().get_logger().warning('current session of {0} status is not eastablished!'.format(self.__target_host))
            return

        pkt = head.proto_head(_type=typedef.PKTTYPE_AGV_SHELL_KEEPALIVE, _id=self.__net_manager.allocate_pkt())
        pkt.set_pkt_size(24)
        stream = pkt.serialize()
        #Logger().get_logger().info('post alive pkt to target {0}'.format(self.__target_host))
        return self.send(stream, pkt.length())

    def post_sysinfo_fixed_request(self):
        if self.__net_status == typedef.NetworkStatus_Closed:
            Logger().get_logger().warning('current session of target:{0} is closed'.format(self.__target_host))
            return -1

        if self.__net_status != typedef.NetworkStatus_Established:
            Logger().get_logger().warning('current session of {0} status is not eastablished!'.format(self.__target_host))
            return

        pkt_id = wait_handler().allocat_pkt_id()
        pkt = head.proto_head(_type=typedef.PKTTYPE_AGV_SHELL_GET_FIXED_SYSINFO, _id=pkt_id)
        pkt.set_pkt_size(24)
        stream = pkt.serialize()
        ret = self.send(stream, pkt.length())
        if ret < 0:
            wait_handler().wait_destory(pkt_id)
            return -1
        return pkt_id

    def recv_keepalive_pkt(self,data,cb):
        (ret, info) = sysinfo.recv_sysinfo_changed(data, cb, 0)
        if ret >= 0:
            self.__mutex.acquire()
            self.__shell_serviceinfo['cpu_percentage'] = info.cpu_percentage.value
            self.__shell_serviceinfo['free_mem'] = info.free_mem.value
            self.__shell_serviceinfo['total_swap'] = info.total_swap.value
            self.__shell_serviceinfo['free_swap'] = info.free_swap.value
            self.__shell_serviceinfo['uptime']=info.uptime.value
            self.__shell_serviceinfo['disk_used_size']=info.disk_used_size.value
            self.__shell_serviceinfo['host_time'] = info.host_time.value
            #print('netio:',info.net_io_rec.value - self.__current_netio_r)
            #print('time_stamp:',self.__timestamp-self.__previous_timestamp)
            
            dec_timestamp = (self.__timestamp-self.__previous_timestamp)/1000
            if dec_timestamp > 0:
                self.__shell_serviceinfo['net_io_rec'] = int((info.net_io_rec.value - self.__current_netio_r)/float(dec_timestamp))
                self.__shell_serviceinfo['net_io_tra'] = int((info.net_io_tra.value - self.__current_netio_t)/float(dec_timestamp))
            #print('net_io_rec',self.__shell_serviceinfo['net_io_rec'])
            #print('net_io_tra',self.__shell_serviceinfo['net_io_tra'])
            self.__current_netio_r=info.net_io_rec.value
            self.__current_netio_t=info.net_io_tra.value
            self.__previous_timestamp=self.__timestamp
            shell_process_name = self.get_shell_process_list()

            process_list = self.__shell_systeminfo.get('process_list')
            last_process_info = deepcopy(process_list)
            # notify_data = list()

            process_name_list = [item.get('process_name') for item in process_list]
            self.__shell_process_info.clear()
            for item in info.process_list:
                if shell_process_name.find(item.name.value) != -1:
                    process_status = (1 if (item.pid.value > 0) else 0)
                    process_list[process_name_list.index(item.name.value)]['status'] = process_status
                    # notify_data.append({'process_name':item.name.value,'status':process_status})
                    self.__shell_process_info.append({'process_name':item.name.value,'process_pid':item.pid.value,
                                                      'run_time':item.run_time.value,'vir_mm':item.vir_mm.value,
                                                      'rss':item.rss.value,'average_cpu':item.average_cpu.value,
                                                      'average_mem':item.average_mem.value})
            self.__mutex.release()
            import operator 
            if operator.eq(process_list,last_process_info) is False:
                if self.__push_notify_cb:
                    self.__push_notify_cb(errtypes.TypeShell_UpdateProcessStatus,{"robot_id":self.__robot_id,"robot_host":self.__target_host,"process_list":process_list})

    def recv_fixed_systeminfo(self,pkt_id,data,cb):
        (ret, info) = sysinfo.recv_sysinfo_fixed(data, cb, 0)
        if ret >= 0:
            self.__shell_systeminfo['robot_id']=self.__robot_id
            self.__shell_systeminfo['robot_host']=self.__target_host
            self.__shell_systeminfo['total_memory'] = info.total_mem.value
            self.__shell_systeminfo['cpu_number'] = info.cpu_num.value
            self.__shell_systeminfo['disk_totoal_size'] = info.disk_total_size.value
            self.__shell_systeminfo['uname'] = info.uname.value
            self.__shell_systeminfo['software_version'] =info.soft_version.value
            self.__shell_systeminfo['config_version'] =info.config_version.value
            self.__shell_systeminfo['lock_status'] =info.status.value
            self.__shell_systeminfo['ntp_server']  = info.ntp_server.value
            cpu_l = list()
            for item in info.cpu_list:
                cpu_info = dict()
                cpu_info['cpu_name']=item.name.value
                cpu_info['cpu_hz']=item.hz.value
                cpu_l.append(cpu_info)
            self.__shell_systeminfo['cpu_list'] = cpu_l
            process_l=list()
            for item in info.process_info:
                process_info = dict()
                process_info['process_name']=item.process_name_.value
                process_info['process_path']=item.process_path_.value
                process_info['process_cmd']=item.process_cmd_.value
                process_info['process_delay']=item.process_delay_.value
                process_info['status'] = 0
                process_l.append(process_info)
            self.__shell_systeminfo['process_list']=process_l
        wait_handler().wait_singal(pkt_id)
        return

    def get_network_status(self):
        return self.__net_status

    def get_host_ipv4(self):
        return self.__target_host

    def get_upgrade_flag(self):
        return self.__upgrading
        
    def set_upgrade(self,flag):
        self.__upgrading = flag
        
    def get_timestamp(self):
        self.__mutex.acquire()
        timestamp=copy.deepcopy(self.__timestamp)
        self.__mutex.release()
        return timestamp

    def get_shell_sys_service_info(self):
        self.__mutex.acquire()
        rev = copy.deepcopy(self.__shell_serviceinfo)
        self.__mutex.release()
        return rev

    def get_connectedtime_value(self):
        self.__mutex.acquire()
        if self.__shell_serviceinfo.__contains__('uptime'):
            value=self.mktime(int(time.time()) - self.__connected_timestamp )
        else:
            value='00:00:00'
        self.__mutex.release()
        return value

    def get_fixed_system_info(self):
        return self.__shell_systeminfo

    def get_shell_version(self):
        return self.__shell_systeminfo.get('software_version')

    def get_shell_process_list(self):
        if 'process_list' not in self.__shell_systeminfo.keys():
            return ''
        return '-'.join([item.get('process_name') for item in self.__shell_systeminfo.get('process_list')])

    def mktime(self,timestamp):
        day = int(timestamp / DAY_SECONDS)
        free_time = timestamp % DAY_SECONDS
        hour = int(free_time / HOUR_SECONDS)
        free_time = free_time % HOUR_SECONDS
        mini = int(free_time / MIN_SECONDS)
        second=free_time % MIN_SECONDS
        if day == 0:
            value = '%02d:%02d:%02d' % (hour,mini,second)
        elif day > 1:
            value = '%d days %02d:%02d:%02d' % (day, hour, mini, second)
        else:
            value= '%d day %02d:%02d:%02d' % (day,hour,mini,second)

        return value

    def get_process_list(self):
        return self.__shell_systeminfo.get('process_list')

    def get_shell_process_detail_list(self):
        return self.__shell_process_info

    def load_log_type(self):
        pkt_id = wait_handler().allocat_pkt_id()
        pkt = head.proto_head(_type=typedef.PKTTYPE_AGV_SHELL_GET_LOG_TYPE, _id=pkt_id)
        pkt.set_pkt_size(24)
        stream = pkt.serialize()
        ret = self.send(stream, pkt.length())
        if ret < 0:
            wait_handler().wait_destory(pkt_id)
            return -1
        return pkt_id

    def recv_log_type(self, pkt_id, data):
        self.__log_type = data
        wait_handler().wait_singal(pkt_id)

    def get_log_types(self):
        return self.__log_type

    def get_log_data(self,task_id, start_time, end_time, types):
        pkt = log.proto_log_condition()
        # pkt.phead.id(task_id)
        pkt.task_id(task_id)
        pkt.start_time(start_time)
        pkt.end_time(end_time)
        if len(types)==0:
            return -1
        for it_type in types:
            pkt_item = log.proto_log_type_item()
            pkt_item.log_type(it_type)
            pkt.vct_log_type.append(pkt_item)
        stream = pkt.serialize()
        ret = self.send(stream, pkt.length())
        return ret

    def register_notify_log_path(self,notify_callback=None):
        if notify_callback is not None:
            global path_notify_callback
            path_notify_callback = notify_callback

    def recv_log_name(self, data):
        global path_notify_callback
        if path_notify_callback is not None:
            path_notify_callback(self.__robot_id,0, data)
        # load_log_path(self.__robot_id,data)
        pass

    def cancle_log_data(self,task_id):
        pkt = log.proto_cancle_log()
        pkt.task_id(task_id)
        stream = pkt.serialize()
        ret = self.send(stream, pkt.length())
        return ret

    def post_modify_file_mutex(self,lock_status):
        packet_modify_file_mutex = sysinfo.proto_msg_int_sync()
        pkt_id = wait_handler().allocat_pkt_id()
        packet_modify_file_mutex.head_.type(typedef.PKTTYPE_AGV_SHELL_MODIFY_FILE_MUTEX)
        packet_modify_file_mutex.head_.id(pkt_id)
        packet_modify_file_mutex.pkt_id(pkt_id)
        packet_modify_file_mutex.msg_int(lock_status)
        packet_modify_file_mutex.head_.size(packet_modify_file_mutex.length())
        return self.send(packet_modify_file_mutex.serialize(),packet_modify_file_mutex.head_.size.value)

    def recv_modify_file_mutex(self,data,cb):
        if cb < 0:
            Logger().get_logger().error("recv modify_file_mutex packet error.")
            return

        packet_file_mutex = sysinfo.proto_msg_int_sync()
        if (packet_file_mutex.build(data, 0) < 0):
            Logger().get_logger().error("recv_modify_file_mutex build  proto_msg_int_sync packet error.")
            return

        if 0 == packet_file_mutex.head_.err.value:
            if packet_file_mutex.msg_int.value == 1:
                self.__shell_systeminfo['lock_status'] = 1
            else:
                self.__shell_systeminfo['lock_status'] = 0

        if self.__push_notify_cb:
            self.__push_notify_cb(errtypes.TypeShell_ModifyFileMutex,{"robot_id":self.__robot_id,"opcode":packet_file_mutex.msg_int.value,"error_code":packet_file_mutex.head_.err.value})

        pass

    def update_ntp_server(self,ntp_host):
        packet_ntp_server = sysinfo.proto_msg()
        pkt_id = wait_handler().allocat_pkt_id()
        packet_ntp_server.head_.type(typedef.PKTTYPE_AGV_SHELL_UPDATE_NTP)
        packet_ntp_server.head_.id(pkt_id)
        packet_ntp_server.msg_str_(ntp_host)
        packet_ntp_server.head_.size(packet_ntp_server.length())
        return self.send(packet_ntp_server.serialize(),packet_ntp_server.head_.size.value)


    def on_update_ntp_server(self,data,cb):
        if cb < 0:
            Logger().get_logger().error("update_ntp_server error.")
            return

        packet_ntp_ack = sysinfo.proto_msg()
        if (packet_ntp_ack.build(data, 0) < 0):
            Logger().get_logger().error("update_ntp_server build  proto_msg packet error.")
            return

        if 0 == packet_ntp_ack.head_.err.value:
            self.__shell_systeminfo['ntp_server'] = packet_ntp_ack.msg_str_.value

        if self.__push_notify_cb:
            self.__push_notify_cb(errtypes.TypeShell_UpdateNtpServer,{"robot_id":self.__robot_id,"error_code":packet_ntp_ack.head_.err.value,"ntp_server":packet_ntp_ack.msg_str_.value})

        pass

    def operate_system_process(self,command):
        from .shproto import proto_process_status
        process_count = len(self.__shell_process_info)
        if process_count <= 0:
            Logger().get_logger().error("Process state anomaly")
            return -1

        process_id = int(0)
        for index in range(process_count):
            process_id = (process_id << 1) + 0x01
        packet_command_process = proto_process_status.proto_command_process()
        pkt_id = wait_handler().allocat_pkt_id()
        packet_command_process.head_.type(typedef.PKTTYPE_AGV_SHELL_PROCESS_COMMAND)
        packet_command_process.head_.id(pkt_id)
        packet_command_process.command_(command)
        packet_command_process.process_id_all_(int(process_id))

        packet_command_process.head_.size(packet_command_process.length())
        return self.send(packet_command_process.serialize(),packet_command_process.head_.size.value)

    def on_recv_process_cmd_ack(self,data,cb):
        if cb < 0:
            Logger().get_logger().error("on_recv_process_cmd_ack error.")
            return

        ack = head.proto_head()
        if (ack.build(data, 0) < 0):
            Logger().get_logger().error("on_recv_process_cmd_ack build  proto_head packet error.")
            return
        pass

    def update_process_list(self,process_list):
        request = proto_process_list.proto_process_list_t()
        request.phead.type(typedef.PKTTYPE_AGV_SHELL_SET_PROCESS_LIST)
        pkt_id = wait_handler().allocat_pkt_id()
        request.phead.id(pkt_id)
        for process_info in process_list:
            process_data = proto_process_list.proto_process_obj_t()
            process_data.process_name_(process_info.get('process_name'))
            process_data.process_path_(process_info.get('process_path'))
            process_data.process_cmd_(process_info.get('process_cmd'))
            process_data.process_delay_(int(process_info.get('process_delay')))
            request.process_list_.append(process_data)
        request.phead.size(request.length())
        return self.send(request.serialize(),request.phead.size.value)

    def on_recv_update_process_list_ack(self,data,cb):
        import operator 
        if cb < 0:
            Logger().get_logger().error("on_recv_update_process_list_ack error.")
            return
        
        ack = proto_process_list.proto_process_list_t()
        if (ack.build(data, 0) < 0):
            Logger().get_logger().error("on_recv_update_process_list_ack build  proto_process_list_ack packet error.")
            return

        if ack.phead.err.value == 0:
            last_process_info = deepcopy(self.__shell_systeminfo.get('process_list'))
            # if last_process_info:
            #     process_status = [{item.get('process_name'):item.get('status')} for item in last_process_info]
            process_l=list()
            for item in ack.process_list_:
                process_info = dict()
                process_info['process_name']=item.process_name_.value
                process_info['process_path']=item.process_path_.value
                process_info['process_cmd']=item.process_cmd_.value
                process_info['process_delay']=item.process_delay_.value
                # status = process_status.get(process_info['process_name'])
                # process_info['status'] = status if status else 0
                process_info['status'] = 0
                process_l.append(process_info)
            self.__shell_systeminfo['process_list']=process_l
            self.__shell_process_info.clear()
            if operator.eq(process_l,last_process_info) is False and self.__push_notify_cb:
                self.__push_notify_cb(errtypes.TypeShell_UpdateProcessStatus,{"robot_id":self.__robot_id,"robot_host":self.__target_host,"process_list":process_l})
                

##################################################以下为fts文件传输协议代码#######################################################


    def push_file_head(self,file_id,file_type,file_name,file_size,ctime,atime,mtime):
        push_head=proto_file.proto_file_head()
        push_head.phead.type(typedef.PKTTYPE_AGV_SHELL_PUSH_FILE_HEAD)
        push_head.phead.id(self.__net_manager.allocate_pkt())
        push_head.file_type(int(file_type))
        push_head.file_name(file_name)
        push_head.file_id(int(file_id))
        push_head.total_size(int(file_size))
        push_head.file_create_time(int(ctime))
        push_head.file_modify_time(int(mtime))
        push_head.file_access_time(int(atime))
        
        push_head.phead.size(push_head.length())
        stream = push_head.serialize()
        return self.send(stream, push_head.length())

        
    def pull_file_head(self,file_id,file_name):
        pull_head=proto_file.proto_request_file_head()
        pull_head.phead.type(typedef.PKTTYPE_AGV_SHELL_READ_FILE_HEAD)
        pull_head.phead.id(self.__net_manager.allocate_pkt())
        pull_head.file_id(int(file_id))
        pull_head.file_path(str(file_name))
        
        pull_head.phead.size(pull_head.length())
        stream = pull_head.serialize()
        return self.send(stream, pull_head.length())
        

    def recv_push_file_head(self,data,cb):
        file_status = proto_file.proto_file_status()
        if cb < file_status.length():
            print("recv_push_file_head receive packet too short, cb[%d]" % cb)
            return -1
        len = 0
        off = file_status.build(data, len)
        if cb != off:
            print("recv_push_file_head build packet failed, cb[%d], off[%d]" % (cb, off))
            return -1
        
        if file_status.phead.err.value !=0 or file_status.error_code.value != 0:
            print("recv_push_file_head packet err, file id[%d], block num[%d], head err[%d], err code[%d]" % \
                    (file_status.file_id.value, file_status.block_num.value, file_status.phead.err.value, file_status.error_code.value))
            if self.__notify_fm is not None:
                self.__notify_fm.file_err(self.__robot_id,file_status.file_id.value,file_status.error_code.value)
            return -1
        #success
        if self.__notify_fm is not None:
            self.__notify_fm.send_file_data(self.__robot_id,file_status.file_id.value, 0) #start from first block, number:0
        else:
            print("session __notify_fm is None")

            
    def recv_pull_file_head(self,data,cb):
        pull_head=proto_file.proto_file_head()
        if cb < pull_head.length():
            print("recv_pull_file_head receive packet too short, cb[%d]" % cb)
            return -1
        len = 0
        off = pull_head.build(data, len)
        if cb != off:
            print("recv_pull_file_head build packet failed, cb[%d], off[%d]" % (cb, off))
            return -1
        
        if pull_head.phead.err.value !=0:
            print("recv_pull_file_head packet err, file id[%d], name[%s], head err[%d]" % \
                    (pull_head.file_id.value, pull_head.file_name.value, pull_head.phead.err.value))
            if self.__notify_fm is not None:
                self.__notify_fm.file_err(self.__robot_id,pull_head.file_id.value,pull_head.phead.err.value)
            return -1
        #success
        if self.__notify_fm is not None:
            self.__notify_fm.create_file_pull_data(self.__robot_id,pull_head) 
        else:
            print("session __notify_fm is None")
        
            
    def push_file_data(self,file_id,block_num,off,data):
        proto_f_data = proto_file.proto_file_data()
        proto_f_data.phead.type(typedef.PKTTYPE_AGV_SHELL_PUSH_FILE_BLOCK)
        proto_f_data.phead.id(self.__net_manager.allocate_pkt())
        proto_f_data.file_id(int(file_id))
        proto_f_data.block_num(int(block_num))
        proto_f_data.file_offset(int(off))
        proto_f_data.file_data(data)
        
        proto_f_data.phead.size(proto_f_data.length())
        stream = proto_f_data.serialize()
        return self.send(stream, proto_f_data.length())
    
    
    def pull_file_data(self,file_id,block_num,off,len):
        proto_r_data = proto_file.proto_request_file_data()
        proto_r_data.phead.type(typedef.PKTTYPE_AGV_SHELL_READ_FILE_BLOCK)
        proto_r_data.phead.id(self.__net_manager.allocate_pkt())
        proto_r_data.file_id(int(file_id))
        proto_r_data.block_num(int(block_num))
        proto_r_data.file_offset(int(off))
        proto_r_data.file_length(int(len))
        
        proto_r_data.phead.size(proto_r_data.length())
        stream = proto_r_data.serialize()
        return self.send(stream, proto_r_data.length())
        

    def recv_push_file_data_reply(self,data, cb):
        pkt = head.proto_head()
        if cb < pkt.length():
            print("recv_push_file_data_reply receive packet too short, cb[%d]" % cb)
            return -1
        if 0 != pkt.err.value:
            print("recv_push_file_data_reply packet head err, head err[%d]" % pkt.err.value)
            return -1
        t_len = 0
        file_status = proto_file.proto_file_status()
        off = file_status.build(data, t_len)
        if cb != off:
            print("recv_push_file_data_reply build packet failed, cb[%d], off[%d]" % (cb, off))
            return -1
        
        if file_status.phead.err.value !=0 or file_status.error_code.value != 0:
            print("recv_push_file_data_reply packet err, file id[%d], block num[%d], head err[%d], err code[%d]" % \
                    (file_status.file_id.value, file_status.block_num.value, file_status.phead.err.value, file_status.error_code.value))
            if self.__notify_fm is not None:
                self.__notify_fm.file_err(self.__robot_id,file_status.file_id.value,file_status.error_code.value)
            return -1
        #success
        if self.__notify_fm is not None:
            self.__notify_fm.send_file_data(self.__robot_id,file_status.file_id.value, (file_status.block_num.value + 1)) #next block
        

    def recv_pull_file_data(self,data,cb):
        pkt = proto_file.proto_file_data()
        if cb < pkt.length():
            print("recv_pull_file_data receive packet too short, cb[%d]" % cb)
            return -1
        t_len = 0
        off = pkt.build(data, t_len)
        if cb != off:
            print("recv_pull_file_data build packet failed, cb[%d], off[%d]" % (cb, off))
            return -1
        
        if pkt.phead.err.value !=0:
            print("recv_pull_file_data packet err, file id[%d], block num[%d], head err[%d]" % \
                    (pkt.file_id.value, pkt.block_num.value, pkt.phead.err.value))
            if self.__notify_fm is not None:
                self.__notify_fm.file_err(self.__robot_id,pkt.file_id.value,pkt.phead.err.value)
            return -1
        #success
        if self.__notify_fm is not None:
            self.__notify_fm.pull_file_data(self.__robot_id,pkt.file_id.value, (pkt.block_num.value + 1), \
                                        pkt.file_offset.value,len(pkt.file_data.value),pkt.file_data.value) #next block
        
        
        
    def file_complete(self,file_id,block_num,error_code=0):
        proto_f_status = proto_file.proto_file_status()
        proto_f_status.phead.type(typedef.PKTTYPE_AGV_SHELL_RW_FILE_STATUS)
        proto_f_status.phead.id(self.__net_manager.allocate_pkt())
        proto_f_status.file_id(int(file_id))
        proto_f_status.block_num(int(block_num))
        proto_f_status.error_code(int(error_code))
        
        proto_f_status.phead.size(proto_f_status.length())
        stream = proto_f_status.serialize()
        return self.send(stream, proto_f_status.length())
        
        
    def recv_file_status(self,data,cb):
        pkt = head.proto_head()
        if cb < pkt.length():
            print("recv_file_status receive packet too short, cb[%d]" % cb)
            return -1
        if 0 != pkt.err.value:
            print("recv_file_status packet head err, head err[%d]" % pkt.err.value)
            return -1
        #finish
        print("recv_file_status success")
        
    def post_a_begin_upgrade(self,f_name,fsize):
        pkt = proto_upgrade.proto_a_upgrade()
        pkt.phead.type(typedef.PKTTYPE_AGV_SHELL_UPGRADE)
        pkt.phead.id(self.__net_manager.allocate_pkt())
        pkt.file_size(int(fsize))
        pkt.file_name(f_name)
        
        pkt.phead.size(pkt.length())
        stream = pkt.serialize()
        return self.send(stream, pkt.length())
        
    
