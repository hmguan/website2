# author:stefan
# data:2018/5/9 8:47


from pynsp.serialize import *
from . import proto_head

class proto_cpu_info(proto_interface):
    def __init__(self):
        super(proto_cpu_info,self).__init__()
        self.name = proto_string()
        self.hz = proto_uint64()

    def length(self)->int:
        return self.name.length()+self.hz.length()

    def serialize(self)->bytes:
        return self.name.serialize() + self.hz.serialize()

    def build(self, data, offset)->int:
        offset= self.name.build(data, offset)
        return self.hz.build(data, offset)

class proto_process_info(proto_interface):
    def __init__(self):
        super(proto_process_info,self).__init__()
        self.name = proto_string()
        self.pid = proto_uint32()
        self.run_time = proto_uint64()
        self.vir_mm = proto_uint64()
        self.rss = proto_uint64()
        self.average_cpu = proto_uint64()
        self.average_mem = proto_uint64()

    def length(self)->int:
        return self.name.length()+\
               self.pid.length()+\
               self.run_time.length()+\
               self.vir_mm.length()+\
               self.rss.length()+\
               self.average_cpu.length()+\
               self.average_mem.length()

    def serialize(self)->bytes:
        return self.name.serialize() + \
               self.pid.serialize() + \
               self.run_time.serialize() + \
               self.vir_mm.serialize() + \
               self.rss.serialize() + \
               self.average_cpu.serialize() + \
               self.average_mem.serialize()

    def build(self, data, offset)->int:
        offset = self.name.build(data, offset)
        offset = self.pid.build(data, offset)
        offset = self.run_time.build(data, offset)
        offset = self.vir_mm.build(data, offset)
        offset = self.rss.build(data, offset)
        offset = self.average_cpu.build(data, offset)
        return self.average_mem.build(data, offset)

class proto_process_config(proto_interface):
    def __init__(self):
        super(proto_process_config, self).__init__()
        self.process_id_= proto_uint32(0)
        self.process_name_= proto_string('')
        self.process_path_= proto_string('')
        self.process_cmd_= proto_string('')
        self.process_delay_= proto_uint32(0)

    def length(self)->int:
        return self.process_id_.length()+\
               self.process_name_.length() + \
               self.process_path_.length() + \
               self.process_cmd_.length() + \
               self.process_delay_.length()

    def serialize(self)->bytes:
        return self.process_id_.serialize()+\
               self.process_name_.serialize() + \
               self.process_path_.serialize() + \
               self.process_cmd_.serialize() + \
               self.process_delay_.serialize()

    def build(self, data, offset=0)->int:
        offset=self.process_id_.build(data, offset)
        offset=self.process_name_.build(data, offset)
        offset=self.process_path_.build(data, offset)
        offset=self.process_cmd_.build(data, offset)
        return self.process_delay_.build(data, offset)

class proto_sysinfo_fixed(proto_interface):
    def __init__(self):
        super(proto_sysinfo_fixed, self).__init__()
        self.phead = proto_head.proto_head()
        self.total_mem = proto_uint64(0)
        self.cpu_num = proto_uint32(0)
        self.cpu_list = proto_vector(proto_cpu_info)
        self.disk_total_size = proto_uint64(0)
        self.uname = proto_string('')
        self.soft_version = proto_string('')
        self.config_version = proto_string('')
        self.process_info=proto_vector(proto_process_config)
        self.status=proto_uint32(0)
        self.ntp_server = proto_string('')


    def length(self)->int:
        return  self.phead.length()+\
                self.total_mem.length() + \
                self.cpu_num.length() + \
                self.cpu_list.length() + \
                self.disk_total_size.length() + \
                self.uname.length() + \
                self.soft_version.length() + \
                self.config_version.length() + \
                self.process_info.length() + \
                self.status.length() +\
                self.ntp_server.length()

    def serialize(self)->bytes:
        return self.phead.serialize()+\
               self.total_mem.serialize() + \
               self.cpu_num.serialize() + \
               self.cpu_list.serialize() + \
               self.disk_total_size.serialize() + \
               self.uname.serialize()+\
               self.soft_version.serialize()+\
               self.config_version.serialize()+\
               self.process_info.serialize()+ \
               self.status.serialize() + \
               self.ntp_server.length()


    def build(self, data, offset=0)->int:
        offset=self.phead.build(data, offset)
        offset=self.total_mem.build(data, offset)
        offset=self.cpu_num.build(data, offset)
        offset=self.cpu_list.build(data, offset)
        offset=self.disk_total_size.build(data, offset)
        offset=self.uname.build(data, offset)
        offset = self.soft_version.build(data, offset)
        offset = self.config_version.build(data, offset)
        offset = self.process_info.build(data, offset)
        offset = self.status.build(data,offset)
        return self.ntp_server.build(data, offset)

class proto_sysinfo_changed(proto_interface):
    def __init__(self):
        super(proto_sysinfo_changed, self).__init__()
        self.phead = proto_head.proto_head()
        self.cpu_percentage = proto_uint32()
        self.free_mem = proto_uint64()
        self.total_swap = proto_uint64()
        self.free_swap = proto_uint64()
        self.disk_used_size = proto_uint64()
        self.uptime = proto_uint64()
        self.host_time = proto_uint64()
        self.net_io_rec=proto_uint64()
        self.net_io_tra=proto_uint64()
        self.process_list = proto_vector(proto_process_info)

    def length(self):
        return self.phead.length()+\
               self.cpu_percentage.length() + \
               self.free_mem.length() + \
               self.total_swap.length() + \
               self.free_swap.length() + \
               self.disk_used_size.length()+\
               self.uptime.length() + \
               self.host_time.length()+\
               self.net_io_rec.length()+\
               self.net_io_tra.length()+\
               self.process_list.length()

    def serialize(self) -> bytes:
        return self.phead.serialize()+\
               self.cpu_percentage.serialize() + \
               self.free_mem.serialize() + \
               self.total_swap.serialize() + \
               self.free_swap.serialize() + \
               self.disk_used_size.serialize() + \
               self.uptime.serialize() + \
               self.host_time.serialize()+\
               self.net_io_rec.serialize()+\
               self.net_io_tra.serialize()+\
               self.process_list.serialize()

    def build(self, data, offset) -> int:
        offset = self.phead.build(data, offset)
        offset = self.cpu_percentage.build(data, offset)
        offset = self.free_mem.build(data, offset)
        offset = self.total_swap.build(data, offset)
        offset = self.free_swap.build(data, offset)
        offset = self.disk_used_size.build(data, offset)
        offset = self.uptime.build(data, offset)
        offset = self.host_time.build(data, offset)
        offset = self.net_io_rec.build(data, offset)
        offset = self.net_io_tra.build(data, offset)
        return self.process_list.build(data, offset)


class proto_msg_int_sync(proto_interface):
    def __init__(self):
        super(proto_msg_int_sync, self).__init__()
        self.head_ = proto_head.proto_head()
        self.pkt_id = proto_int32(0)
        self.msg_int = proto_int32(0)

    def length(self):
        return self.head_.length() + self.pkt_id.length() + self.msg_int.length()

    def serialize(self)->bytes:
        return self.head_.serialize() + self.pkt_id.serialize() + self.msg_int.serialize()

    def build(self,data,offset) -> int:
        offset = self.head_.build(data,offset)
        offset = self.pkt_id.build(data,offset)
        return self.msg_int.build(data,offset)

def recv_sysinfo_fixed(data, len,offset)->tuple:
    tmp = proto_sysinfo_fixed()
    offset = tmp.build(data, offset)
    ret = 0
    if (offset != tmp.length()):
        ret = -1
    return (ret, tmp)

def recv_sysinfo_changed(data, len,offset)->tuple:
    tmp = proto_sysinfo_changed()
    offset = tmp.build(data, offset)
    ret =0
    if(offset != tmp.length()):
        ret =-1
    return (ret,tmp)



if __name__ =='__main__':
    test = proto_sysinfo_changed()
    test = proto_sysinfo_fixed()


