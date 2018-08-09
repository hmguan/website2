###################################定义所有通知错误类型#############################

#用户管理错误定义
TypeError_UserNoExist =  0x00000501
TypeError_UserWrongPWD = 0x00000502
TypeError_UserLogined =  0x00000503

#shell模块与前端socketio交互类型定义
TypeShell_WebSokcetConnect = 0x00000000
TypeShell_NewArrival = 0x00000101
TypeShell_Offline = 0x00000102
TypeShell_UpdateSoftware=0x00000103
TypeShell_ConnectException=0x00000104
TypeShell_ModifyFileMutex =0x00000105
TypeShell_Blackbox_Log=0x00000106
TypeShell_Blackbox_None=0x00000107
TypeShell_UpdateNtpServer=0x00000108
TypeShell_UpdateProcessStatus = 0x00000109
TypeShell_UpdateProcessList = 0x0000010a

#mt与前端交互类型定义
TypeMT_Error=0x00000601
TypeMT_Offline=0x00000602

###############################以下定义http状态响应码############################
HttpResponseCode_Normal=0

#公共错误状态码
HttpResponseCode_UserNotLogin=1
HttpResponseCode_FailedVerifyToken=2
HttpResponseCode_InvaildEvent=3
HttpResponseCode_InvaildParament=4
HttpResponseCode_InvaildGroup_Name=30
HttpResponseCode_UserNotLogined=31


#用户管理相关错误状态码[100,200)
HttpResponseCode_UserExisted=100
HttpResponseCode_Sqlerror=101
HttpResponseCode_InvaildUserOrPwd=102
HttpResponseCode_UserNotExisted=103
HttpResponseCode_InvaildToken=104
HttpResponseCode_PermissionDenied=105
HttpResponseCode_TimeoutToken=106
HttpResponseCode_UserOffline=107



#用户管理错误状态码区间[200,300)


#shell模块错误状态码区间[300,400)


#MT模块错误状态码区间[600,700)

#升级包
HttpResponseCode_UPLOADEXCEPTIONERROR=50
HttpResponseCode_NOFILE=51
HttpResponseCode_EXISTFILE=51
HttpResponseCode_InvaildPath = 52
HttpResponseCode_FileBusy = 53
#不在线
HttpResponseCode_RobotOffLine = 70

HttpResponseCode_NotFound=404
HttpResponseCode_ServerError=500


#############################以下定义http响应消息###############################
HttpResponseMsg_Normal='success'

HttpResponseMsg_UserNotLogin='current operate user is not login'
HttpResponseMsg_InvaildEvent='invaild input event'
HttpResponseMsg_InvaildParament='invalid input parament'
HttpResponseMsg_InvaildPath='File Not Found'
HttpResponseMsg_Failed='failed'
HttpResponseMsg_FileNotExist = 'Cannot find file'
HttpResponseMsg_RobotOffLine = 'Robot Not OnLine'
HttpResponseMsg_Timeout='service timeout'
HttpRequestMsg_UserNotExisted ='user does not exist'
HttpResponseMsg_FileBusy = 'The file has been opened'



