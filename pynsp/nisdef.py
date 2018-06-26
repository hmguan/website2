from ctypes import *
import sys

# common network events
EVT_CREATED         = 0x0001    # created 
EVT_PRE_CLOSE       = 0x0002    # ready to close
EVT_CLOSED          = 0x0003    # has been closed 
EVT_RECEIVEDATA     = 0x0004    # receive data
EVT_SENDDATA        = 0x0005    # sent data
EVT_DEBUG_LOG       = 0x0006    # report debug information 
EVT_EXCEPTION       = 0xFFFF    # exceptions

# TCP events
EVT_TCP_ACCEPTED    = 0x0013   # has been Accepted 
EVT_TCP_CONNECTED   = 0x0014  # success connect to remote 

# option to get link address
LINK_ADDR_LOCAL     = 0x0001   # get local using endpoint pair
LINK_ADDR_REMOTE    = 0x0002   # get remote using endpoint pair

class Tcp(Structure):
    _fields_ = [                  
        ("Link", c_int)       
    ]

class Udp(Structure):
    _fields_ = [                  
        ("Link", c_int)       
    ]

class Ln(Union):
    _fields_ = [                  
        ("UdpLink", Udp),
        ("TcpLink", Tcp)    
    ]
    

class nis_event_t(Structure):
    _fields_ = [                  
        ("Event", c_int),             
        ("Link", Ln)              
    ]

class TcpPacket(Structure):
    _fields_ = [                  
        ("Data", POINTER(c_char) ),
        ("Size", c_int)              
    ]

class Accept(Structure):
    _fields_ = [                  
        ("AcceptLink", c_int)              
    ]

class NSException(Structure):
    _fields_ = [                  
        ("SubEvent", c_int),             
        ("ErrorCode", c_int)              
    ]

class LinkOption(Structure):
    _fields_ = [                  
        ("OptionLink", c_int),             
    ]

class DebugLog(Structure):
    _fields_ = [                  
        ("logstr", c_char_p),             
    ]

class es(Union):
    _fields_ = [                  
        ("Packet", TcpPacket),  
        ("Accept", Accept), 
        ("Exception", NSException), 
        ("LinkOption", LinkOption), 
        ("DebugLog", DebugLog)           
    ]

class tcp_data_t(Structure):
    _fields_ = [                  
        ("e", es),             
    ]

# creat object for type c-style callback
# very importent, if the parameter is c-style pointer, python code need key word 'POINTER' to mark it
tcpio_callback_t = CFUNCTYPE(None, POINTER(nis_event_t), POINTER(tcp_data_t))
tcptst_parse_t = CFUNCTYPE(c_int, POINTER(c_byte), c_int, POINTER(c_int))
tcptst_build_t = CFUNCTYPE(c_int, POINTER(c_byte), c_int)
tcp_packet_maker_t = CFUNCTYPE(c_int, POINTER(c_byte), c_int, POINTER(c_byte))

class tcp_tst_t(Structure):
    _fields_ = [                  
        ("parser", tcptst_parse_t),             
        ("builder", tcptst_build_t),
        ("cb", c_int)      
    ]

# UDP impls
UDP_FLAG_NONE           = 0
UDP_FLAG_UNITCAST       = UDP_FLAG_NONE
UDP_FLAG_BROADCAST      = 1
UDP_FLAG_MULTICAST      = 2

class UdpPacket(Structure):
    _fields_ = [                  
        ("Data", POINTER(c_char) ),
        ("Size", c_int),
        ("RemoteAddress", c_char * 16),
        ("RemotePort", c_ushort)
    ]

class ues(Union):
    _fields_ = [
        ("Packet", UdpPacket),  
        ("Exception", NSException), 
        ("LinkOption", LinkOption), 
        ("DebugLog", DebugLog)   
    ]

class udp_data_t(Structure):
    _fields_ = [
        ("e", ues)
    ]

udpio_callback_t = CFUNCTYPE(None, POINTER(nis_event_t), POINTER(udp_data_t))

# global cdll object for pynsp
if 'linux' == sys.platform:
    solib = cdll.LoadLibrary('/usr/local/lib64/nshost.so')
else:
    solib = cdll.LoadLibrary('./nshost.so')