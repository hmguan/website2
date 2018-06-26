from . import proto_head as phead
from pynsp.serialize import *
from . import proto_typedef

class proto_request_file_head(proto_interface):
    def __init__(self):
        super(proto_request_file_head,self).__init__()
        self.phead=phead.proto_head()
        self.file_path=proto_string('')
        self.file_id=proto_uint64(0)

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.file_path.length() + self.file_id.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.file_path.serialize() + self.file_id.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.file_path.build(data, off)
        return self.file_id.build(data, off)

class proto_file_head(proto_interface):
    def __init__(self):
        super(proto_file_head,self).__init__()
        self.phead=phead.proto_head()
        self.file_type=proto_uint32(0)
        self.file_name=proto_string('')
        self.file_id=proto_uint64(0)
        self.total_size=proto_uint64(0)
        self.file_create_time=proto_uint64(0)
        self.file_modify_time=proto_uint64(0)
        self.file_access_time=proto_uint64(0)

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.file_type.length() + self.file_id.length() + self.file_name.length() + self.total_size.length() \
                + self.file_create_time.length() + self.file_modify_time.length() + self.file_access_time.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.file_type.serialize() + self.file_name.serialize() + \
                self.file_id.serialize() + self.total_size.serialize() + self.file_create_time.serialize() + \
                self.file_modify_time.serialize() + self.file_access_time.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.file_type.build(data, off)
        off = self.file_name.build(data, off)
        off = self.file_id.build(data, off)
        off = self.total_size.build(data, off)
        off = self.file_create_time.build(data, off)
        off = self.file_modify_time.build(data, off)
        off = self.file_access_time.build(data, off)
        return off

class proto_request_file_data(proto_interface):
    def __init__(self):
        super(proto_request_file_data,self).__init__()
        self.phead=phead.proto_head()
        self.block_num=proto_uint32(0)
        self.file_length=proto_uint32(0)
        self.file_id=proto_uint64(0)
        self.file_offset=proto_uint64(0)

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.block_num.length() + self.file_length.length() + self.file_id.length() + self.file_offset.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.block_num.serialize() + self.file_length.serialize() + self.file_id.serialize() + self.file_offset.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.block_num.build(data, off)
        off = self.file_length.build(data, off)
        off = self.file_id.build(data, off)
        off = self.file_offset.build(data, off)
        return off

class proto_file_data(proto_interface):
    def __init__(self):
        super(proto_file_data,self).__init__()
        self.phead=phead.proto_head()
        self.block_num=proto_uint32(0)
        self.file_id=proto_uint64(0)
        self.file_offset=proto_uint64(0)
        self.file_data=proto_binary()

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.block_num.length() + self.file_id.length() + self.file_offset.length() + self.file_data.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.block_num.serialize() + self.file_id.serialize() + self.file_offset.serialize() + self.file_data.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.block_num.build(data, off)
        off = self.file_id.build(data, off)
        off = self.file_offset.build(data, off)
        off = self.file_data.build(data, off)
        return off

class proto_file_status(proto_interface):
    def __init__(self):
        super(proto_file_status,self).__init__()
        self.phead=phead.proto_head()
        self.error_code=proto_int32(0)
        self.block_num=proto_uint32(0)
        self.file_id=proto_uint64(0)

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.error_code.length() + self.block_num.length() + self.file_id.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.error_code.serialize() + self.block_num.serialize() + self.file_id.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.error_code.build(data, off)
        off = self.block_num.build(data, off)
        off = self.file_id.build(data, off)
        return off

