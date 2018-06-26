# author:stefan
# data:2018/5/3 15:38
from . import proto_head
from pynsp.serialize import *


class proto_process_status_t(proto_interface):
    def __init__(self):
        super(proto_process_status_t,self).__init__()
        self.phead = proto_head.proto_head()
        self.cmd_s_ = proto_int8()
        self.status_ = proto_int8()
        self.agv_shell_reply_ = proto_int8()
        self.cmd_end_ = proto_int8()
        self.robot_time_ = proto_uint64()
        self.vcu_enable_ = proto_int32()

    def length(self)->int:
        return self.phead.length()+\
               self.cmd_s_.length()+\
               self.status_.length()+\
               self.agv_shell_reply_.length()+\
               self.cmd_end_.length()+\
               self.robot_time_.length()+\
               self.vcu_enable_.length()

    def serialize(self)->bytes:
        return self.phead.serialize()+\
               self.cmd_s_.serialize()+\
               self.status_.serialize()+\
               self.agv_shell_reply_.serialize()+\
               self.cmd_end_.serialize()+\
               self.robot_time_.serialize()+\
               self.vcu_enable_.serialize()

    def build(self, data,len,offset = 0)->int:
        offset = self.phead.build(data, offset)
        offset = self.cmd_s_.build(data, offset)
        offset = self.status_.build(data, offset)
        offset = self.agv_shell_reply_.build(data, offset)
        offset = self.cmd_end_.build(data, offset)
        offset = self.robot_time_.build(data, offset)
        return self.vcu_enable_.build(data, offset)


def recv_process_status(data,len,offset):
    test = proto_process_status_t()
    test.build(data, len, offset)
    return test







