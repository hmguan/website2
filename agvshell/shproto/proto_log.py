from . import proto_head as phead
from pynsp.serialize import *
from . import proto_typedef

class proto_log_type_item(proto_interface):
    def __init__(self):
        super(proto_log_type_item,self).__init__()
        self.phead=phead.proto_head()
        self.log_type=proto_string('')

    def length(self):
        return self.phead.length()+self.log_type.length()

    def serialize(self):
        return self.phead.serialize()+self.log_type.serialize()

    def build(self, data, offset)->int:
        off=self.phead.build(data,offset)
        off=self.log_type.build(data,off)
        return off

class proto_log_type_vct(proto_interface):
    def __init__(self):
        super(proto_log_type_vct,self).__init__()
        self.phead=phead.proto_head()
        self.log_type_vct = proto_vector(TYPE = proto_log_type_item)

    def length(self)->int:
        return self.phead.length() + self.log_type_vct.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.log_type_vct.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.log_type_vct.build(data, off)
        return off


class proto_log_condition(proto_interface):
    def __init__(self):
        super(proto_log_condition, self).__init__()
        self.phead=phead.proto_head(_type=proto_typedef.PKTTYPE_AGV_SHELL_GET_LOG_FILE_NAME)
        self.task_id=proto_int()
        self.start_time=proto_string('')
        self.end_time=proto_string('')
        self.vct_log_type = proto_vector(TYPE=proto_log_type_item)

    def length(self) -> int:
        return self.phead.length()+self.task_id.length()+self.start_time.length()+self.end_time.length()+self.vct_log_type.length()

    def serialize(self)->bytes:
        return self.phead.serialize()+self.task_id.serialize()\
               +self.start_time.serialize()\
               +self.end_time.serialize()\
               +self.vct_log_type.serialize()

    def build(self, data, offset)->int:
        offset= self.phead.build(data, offset)
        offset=self.task_id.build(data,offset)
        offset = self.start_time.build(data, offset)
        offset=self.end_time.build(data,offset)
        return self.vct_log_type.build(data, offset)

class proto_logs_file_path(proto_interface):
    def __init__(self):
        super(proto_logs_file_path, self).__init__()
        self.phead = phead.proto_head(_type=proto_typedef.PKTTYPE_AGV_SHELL_CANCEL_GET_LOG)
        self.task_id = proto_uint32()
        self.vct_log_file_name=proto_vector(TYPE=proto_string)

    def length(self):
        return self.phead.length()+self.task_id.length()+self.vct_log_file_name.length()

    def serialize(self):
        return  self.phead.serialize()+self.task_id.serialize()+self.vct_log_file_name.serialize()

    def build(self, data, offset):
        off=self.phead.build(data,offset)
        off=self.task_id.build(data,off)
        off=self.vct_log_file_name.build(data,off)
        return off

class proto_cancle_log(proto_interface):
    def __init__(self):
        super(proto_cancle_log, self).__init__()
        self.phead = phead.proto_head()
        self.task_id=proto_int()

    def length(self):
        return self.phead.length()+self.task_id.length()

    def serialize(self):
        return  self.phead.serialize()+self.task_id.serialize()

    def build(self, data, offset):
        off=self.phead.build(data,offset)
        off=self.task_id.build(data,off)
        return off



