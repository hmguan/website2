###################################定义所有通知错误类型#############################

#用户管理错误定义
TypeError_UserNoExist =  0x00000501
TypeError_UserWrongPWD = 0x00000502
TypeError_UserLogined =  0x00000503

#shell模块与前端socketio交互类型定义
TypeShell_SokcetIOConnect = 0x00000100
TypeShell_NewArrival = 0x00000101
TypeShell_Offline = 0x00000102
TypeShell_UpdateSoftware=0x00000103
TypeShell_ConnectException=0x00000104

#mt与前端交互类型定义
TypeMT_Error=0x00000601
TypeMT_Offline=0x00000602


###############################以下定义http状态响应码############################
HttpResponseCode_Failed=-1
HttpResponseCode_Normal=0
HttpResponseCode_InvaildEvent=20
HttpResponseCode_InvaildParament=21
HttpResponseCode_TimeOut=22
#用户管理
HttpResponseCode_InvaildToken=23
HttpResponseCode_TimeoutToken=24
HttpResponseCode_InvaildUserAndPwd=25
HttpResponseCode_UserOffline=26
HttpResponseCode_UserExisted=27
HttpResponseCode_UserNotExisted=28
HttpResponseCode_UserNotLogined=29
HttpResponseCode_InvaildGroup_Name=30
#升级包
HttpResponseCode_UPLOADEXCEPTIONERROR=50
HttpResponseCode_NOFILE=51

HttpResponseCode_NotFound=404
HttpResponseCode_ServerError=500



#############################以下定义http响应消息###############################
HttpResponseMsg_Normal='success'
HttpResponseMsg_InvaildParament='invalid input parament'
HttpResponseMsg_Failed='failed'
