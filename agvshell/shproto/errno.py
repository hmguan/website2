'''
错误码定义
'''

#errno
#system errno
ERRNO_EACCES = 13
ERRNO_EINVAL = 22


#user define errno
USER_DEFINE_ERR_FLAG = 0x00010000
SECCUSS_FLAG = USER_DEFINE_ERR_FLAG
ERRNO_FILE_NORMAL = 0x00010001

ERRNO_FILE_OPEN = 0x00010001
ERRNO_FILE_WRITE = 0x00010002
ERRNO_FILE_CREATE = 0x00010002
ERRNO_FILE_CANCLE = 0x00010003
ERRNO_FILE_TIMEOUT = 0x00010003


ERRNO_FILE_UPGRADE = 0x00010010
ERRNO_FILE_SESSION_CLOSE = 0x00010011
ERRNO_ROBOT_CONNECT = 0x00010012
ERRNO_FILE_TRANIMIT = 0X00010013

#system
g_err_str = {}
g_err_str[ERRNO_EACCES] = "Permission denied"
g_err_str[ERRNO_EINVAL] = "Invalid argument"

#user define
g_err_str[ERRNO_FILE_OPEN] = "Open file error"
g_err_str[ERRNO_FILE_WRITE] = "Write file error"
g_err_str[ERRNO_FILE_CREATE] = "Create file error"
g_err_str[ERRNO_FILE_CANCLE] = "Canle file transfrom"
g_err_str[ERRNO_FILE_TIMEOUT] = "File transfrom timeout"
g_err_str[ERRNO_FILE_UPGRADE] = "Robot is upgrading, cannot transfrom upgrade package again"
g_err_str[ERRNO_FILE_SESSION_CLOSE] = "File transfrom error, session closed"
g_err_str[ERRNO_ROBOT_CONNECT] = "Robot is offline, check session status"
g_err_str[ERRNO_FILE_TRANIMIT] = "File transmit error"
