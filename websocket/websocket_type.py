
#the websocket package type value
WS_CONTINUATION_FRAME=0x00
WS_TEXT_FRAME=0x01
WS_BINARY_FRAME=0x02
WS_CLOSEF_RAME=0x08
WS_PING_FRAME=0x09
WS_PONG_FRAME=0x0A
WS_EMPTY_FRAME=0xF0
WS_ERROR_FRAME=0xF1
WS_OPENINGFRAME=0xF3

#the status code of close websocket
# 1000 正常关闭
# 1001 端点丢失，如服务器宕机或浏览器切换其他页面
# 1002 协议错误
# 1003 数据类型错误（例如端点只能处理文本，但传来了二进制消息）
# 1004 保留
# 1005 保留，禁止由端点发送此类型关闭帧，它是用来当端点没有表明关闭码时的默认关闭码。
# 1006 保留，禁止由端点发送此类型关闭帧，它是用来当端点未发送关闭帧，连接异常断开时使用。
# 1007 数据内容错误（如在text帧中非utf-8编码的数据）
# 1008 端点已接收消息，但违反其策略。当没有更好的关闭码（1003或1009）的时候用此关闭码或者不希望显示错误细节。
# 1009 内容过长
# 1010 客户端期望服务器协商一个或多个扩展，但这些扩展并未在WebSocket握手响应中返回。
# 1011 遇到未知情况无法执行请求
# 1015 保留，禁止由端点发送此类型关闭帧，它会在TLS握手失败（如证书验证失败）时返回。
WS_CLOSE_NORMAL='\x03\xe8'
WS_CLOSE_ENDPOINT_MISS='\x03\xe9'
WS_CLOSE_PROTOCOL_ERR='\x03\xea'
WS_CLOSE_DATATYPE_ERR='\x03\xeb'
WS_CLOSE_RESERVE='\x03\xec'
WS_CLOSE_NO_CODE='\x03\xed'
WS_CLOSE_NO_CLOSE='\x03\xee'
