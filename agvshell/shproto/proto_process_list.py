# author:stefan
# data:2018/5/3 15:37
from . import proto_head
from pynsp.serialize import *
from . import proto_typedef as typedef

class proto_process_obj_t(proto_interface):
    def __init__(self):
        super(proto_process_obj_t,self).__init__()

        self.process_id_ = proto_int32()
        self.process_name_ = proto_string()
        self.process_path_ = proto_string()
        self.process_cmd_ = proto_string()
        self.process_delay_ = proto_int32()

    def length(self)->int:
        return self.process_id_.length()+\
               self.process_name_.length()+\
               self.process_path_.length()+\
               self.process_cmd_.length()+\
               self.process_delay_.length()

    def serialize(self)->bytes:
        return self.process_id_.serialize()+\
               self.process_name_.serialize()+\
               self.process_path_.serialize()+\
               self.process_cmd_.serialize()+\
               self.process_delay_.serialize()

    def build(self, data,offset=0)->int:
        offset = self.process_id_.build(data, offset)
        offset = self.process_name_.build(data, offset)
        offset = self.process_path_.build(data, offset)
        offset = self.process_cmd_.build(data, offset)
        return self.process_delay_.build(data, offset)


class proto_process_list_t(proto_interface):
    def __init__(self):
        super(proto_process_list_t, self).__init__()

        self.phead = proto_head.proto_head(_type=typedef.PKTTYPE_AGV_SHELL_SET_PROCESS_LIST)
        self.pkt_id_ = proto_int32(0)
        self.process_list_=proto_vector(proto_process_obj_t)

    def length(self)->int:
        return self.pkt_id_.length()+self.phead.length()+self.process_list_.length()

    def serialize(self)->bytes:
        return self.phead.serialize()+self.pkt_id_.serialize()+self.process_list_.serialize()

    def build(self,data,offset = 0)->int:
        offset = self.phead.build(data, offset)
        offset = self.pkt_id_.build(data, offset)
        return self.process_list_.build(data, offset)


class proto_process_list_request_t(proto_interface):
    def __init__(self):
        super(proto_process_list_request_t, self).__init__()
        self.phead = proto_head.proto_head(_type=typedef.PKTTYPE_PROCESSLIST)
        self.pkt_id_ = proto_int32(0)

    def length(self) -> int:
        return self.pkt_id_.length() + self.phead.length()

    def serialize(self) -> bytes:
        return self.phead.serialize()+self.pkt_id_.serialize()

    def build(self, data, offset=0) -> int:
        offset = self.phead.build(data, offset)
        return self.pkt_id_.build(data, offset)


#发送列表请求
def post_process_list_request():
    request = proto_process_list_request_t()
    return  request.serialize(),request.length()

#收到应答序列化
def recv_process_list(data,len,offset=0):
    process_list_obj = proto_process_list_t()
    process_list_obj.build(data,offset)
    return process_list_obj.process_list_


class proto_process_list_ack(proto_interface):
    """docstring for proto_common_stream"""
    def __init__(self):
        super(proto_common_stream, self).__init__()
        self.head_ = proto_head.proto_head()
        self.pkt_id_ = proto_int32(0)
        self.common_stream_ = proto_string()
        self.process_list_=proto_vector(TYPE=proto_process_obj_t)

    def length(self):
        return self.head_.length() + self.pkt_id.length() + self.common_stream.length() + self.process_list_.length()

    def serialize(self)->bytes:
        return self.head_.serialize() + self.pkt_id.serialize() + self.common_stream.serialize()+ self.process_list_.serialize()

    def build(self,data,offset) -> int:
        offset = self.head_.build(data,offset)
        offset = self.pkt_id.build(data,offset)
        offset = self.common_stream.build(data,offset)
        return self.process_list_.build(data,offset)




