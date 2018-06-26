from pynsp.serialize import *
from . import proto_head as protohead
from . import proto_typedef

kAgvShellProto_LocalInfo = 0x00010204

class agvsh_local_report(proto_interface):
	def __init__(self):
		super(agvsh_local_report, self).__init__()
		self.phead = protohead.proto_head()
		self.sh_port = proto_uint32()
		self.ftp_port = proto_uint32()
		self.mac = proto_string()

	def __del__(self):
		pass

	def length(self)->int:
		return self.phead.length() + self.sh_port.length() + self.ftp_port.length() + self.mac.length()

	def serialize(self)->int:
		return self.phead.serialize() + self.sh_port.serialize() + self.ftp_port.serialize() + self.mac.serialize()

	def build(self, data, offset)->int:
		off = self.phead.build(data, offset)
		off = self.sh_port.build(data, off)
		off = self.ftp_port.build(data, off)
		off = self.mac.build(data, off)
		return off