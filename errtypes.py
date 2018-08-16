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
HttpResponseCode_MutexTimeout=5
HttpResponseCode_InvaildGroup_Name=30

#用户管理相关错误状态码[100,200)
HttpResponseCode_UserExisted=100
HttpResponseCode_Sqlerror=101
HttpResponseCode_InvaildUserOrPwd=102
HttpResponseCode_UserNotExisted=103
HttpResponseCode_InvaildToken=104
HttpResponseCode_PermissionDenied=105
HttpResponseCode_TimeoutToken=106
HttpResponseCode_UserOffline=107
HttpResponseCode_Loginout=108
HttpResponseCode_UpdatePWD=109
HttpResponseCode_RootOper=110

#文件管理错误状态码区间[200,300)
HttpResponseCode_FileNotExist = 202
HttpResponseCode_NoAuthority = 203
HttpResponseCode_FileBusy = 204
HttpResponseCode_DateBasePacketIdNotFound = 205
HttpResponseCode_NotFileOwner = 206
HttpResponseCode_NOEXISTPackage=207
HttpResponseCode_NOFILE=208
HttpResponseCode_UPLOADEXCEPTIONERROR=209
HttpResponseCode_FailedRemoveFile=210

#shell模块错误状态码区间[300,400)
HttpResponseCode_DatabaseRecordAbnormity = 300
HttpResponseCode_IDRepetition = 301
HttpResponseCode_TaskFull = 302
HttpResponseCode_RobotOffLine =303
HttpResponseCode_TaskNotExist = 304

HttpResponseCode_BlackboxSendFailed=381
HttpResponseCode_BlackboxReTask=382
HttpResponseCode_BlackboxNoTask=383
HttpResponseCode_BlackboxWaitTar=384
HttpResponseCode_BlackboxDeleteFailed=385
HttpResponseCode_BlackboxDbNoFile=386
HttpResponseCode_BlackboxNoDownlownFile=387
HttpResponseCode_BlackboxQueryDbFailed=388
HttpResponseCode_BlackboxNoRecord=389
#不在线

HttpResponseCode_NotFound=404
HttpResponseCode_ServerError=500

#MT模块错误状态码区间[600,700)
HttpResponseCode_MtOffline=601
HttpResponseCode_MtProtoErr=602
HttpResponseCode_MtQueryTimeout=603
HttpResponseCode_MtMissVariate=604

#############################以下定义http响应消息###############################
HttpResponseMsg_Normal='success'

HttpResponseMsg_UserNotLogin='current operate user is not login'
HttpResponseMsg_InvaildEvent='invaild input event'
HttpResponseMsg_InvaildParament='invalid input parament'
HttpResponseMsg_InvaildPath='File Not Found'
HttpResponseMsg_Failed='failed'
HttpResponseMsg_FileNotExist = 'Cannot find file'
HttpResponseMsg_Timeout='service timeout'
HttpRequestMsg_UserNotExisted ='user does not exist'

#shell 模块
HttpResponseMsg_DatabaseRecordAbnormity = 'Database record abnormity'
HttpResponseMsg_IDRepetition = 'ID repeat in the request'
HttpResponseMsg_TaskFull = 'Task to reach maximum'
HttpResponseMsg_RobotOffLine = 'Robot not OnLine'
HttpResponseMsg_TaskNotExist ='The task does not exist'

#文件管理
HttpResponseMsg_NoAuthority = 'No authority'
HttpResponseMsg_FileBusy = 'The file has been opened'
HttpResponseMsg_DateBasePacketIdNotFound = 'The packetid can not be found in the database'
HttpResponseMsg_NotFileOwner = 'Not File Owner'
HttpResponseCodeMsg_NoFileSelect='There is not file been selected'

#用户管理相关错误状态码错误说明
HttpResponseCodeMsg_UserExisted='user is existed'
HttpResponseCodeMsg_Sqlerror='sql error'
HttpResponseCodeMsg_InvaildUserOrPwd='username or password is wrong'
HttpResponseCodeMsg_UserNotExisted='user is not existed'
HttpResponseCodeMsg_InvaildToken='token signature expired'
HttpResponseCodeMsg_PermissionDenied='permission denied'
HttpResponseCodeMsg_TimeoutToken='token bad signature'
HttpResponseCodeMsg_UserOffline='offline'

#MT相关错误状态码说明
HttpResponseMsg_MtOffline = 'Mt offline'
HttpResponseMsg_MtProtoErr = 'Mt protocol error'
HttpResponseMsg_MtQueryTimeout = 'mt query data timeout'
HttpResponseMsg_MtMissVariate = 'The variable cannot be found'

#Blackbox相关错误状态码说明
HttpResponseMsg_BlackboxReTask='the user already has task'
HttpResponseMsg_BlackboxSendFailed='All agvs failed to be sent'
HttpResponseMsg_BlackboxNoTask='can not find the task'
HttpResponseMsg_BlackboxWaitTar='a log file is being tar '
HttpResponseMsg_BlackboxDeleteFailed='delete log failed '
HttpResponseMsg_BlackboxDbNoFile='the file cannot be found in the database'
HttpResponseMsg_BlackboxNoDownlownFile='the downlown file cannot be found'
HttpResponseMsg_BlackboxQueryDbFailed='query datebase failed'
HttpResponseMsg_BlackboxNoRecord ="no sql record"
#升级包管理
HttpResponseCodeMsg_NOEXISTPackage='package is not existed'
HttpResponseCodeMsg_FailedRemoveFile='failed tp remove file'
