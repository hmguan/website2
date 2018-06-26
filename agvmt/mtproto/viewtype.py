
kVarFixedObject_MotionTemplateFramwork = 0 # MT 框架预留
kVarFixedObject_Navigation = 1 #导航
kVarFixedObject_Vehide=2 # 底盘
kVarFixedObject_Operation=3 # 操作
kVarFixedObject_UserDefinition=4 # 用户定义区
kVarFixedObject_OptPar=5 # 操作参数
kVarFixedObject_Map=6 # 地图
kVarFixedObject_ErrorCollecter=7 # 错误采集
kVarFixedObject_SaftyProtec=8 # 安全防护
kVarFixedObject_InternalDIO=9 # 内部DIO/充电信息和指令
kVarFixedObject_Virtual = 10 # virtual object with only functional head
kVarFixedObject_Localization = kVarFixedObject_Virtual,
kVarReserved_MaximumFunction = 20 # 最大预留区间




kVarType_MotionTemplateFramwork = 0  # MT 框架预留
# var
kVarType_Vehicle = 1 # 整车
kVarType_Navigation = 2  # 导航
kVarType_Operation = 3  #定制操作
kVarType_UserDefined = 4  #用户指定
kVarType_SWheel = 5  #逻辑转向轮
kVarType_DWheel = 6  # 逻辑驱动轮
kVarType_SDDExtra = 7  # 逻辑 SDD 架构附加信息
kVarType_DriveUnit = 8  # 驱动单元
kVarType_Map = 9  # 地图
kVarType_OperationTarget =10  # 操作目标参数表
kVarType_Localization = 11

# dev
kVarType_CanBus = 0x100  # CAN 总线设备
kVarType_Copley = 0x101   # COPLEY 设备
kVarType_Elmo = 0x102   #ELMO 设备
kVarType_DIO = 0x103  # DIO 设备
kVarType_Moons = 0x104   # MOONS (步进电机)
kVarType_AngleEncoder = 0x105    # 角度编码器
kVarType_Curtis = 0x106    # 柯蒂斯控制器 设备
kVarType_VoiceDevice = 0x107   # 音响设备
kVarType_PrivateDriver = 0x108   #

# memnetdev
kVarType_OmronPLC = 0x500    #欧姆龙PLC网络设备
kVarType_ModBus_TCP = 0x501   #网络协议的 modbus-TCP

# logic
kVarType_ErrorHandler = 0x1000
kVarType_SafetyProtec = 0x1001

# maximum
kVarType_MaximumFunction = 0x7FFF

typeDict={0:'kVarType_MotionTemplateFramwork',1:'kVarType_Vehicle',2:'kVarType_Navigation',3:'kVarType_Operation',4:'kVarType_UserDefined',
          5:'kVarType_SWheel',6:'kVarType_DWheel',7:'kVarType_SDDExtra',8:'kVarType_DriveUnit',9:'kVarType_Map',10:'kVarType_OperationTarget',
          11:'kVarType_Localization',0x100:'kVarType_CanBus',0x101:'kVarType_Copley',0x102:'kVarType_Elmo',0x103:'kVarType_DIO',0x104:'kVarType_Moons',
          0x105:'kVarType_AngleEncoder',0x106:'kVarType_Curtis',0x107:'kVarType_VoiceDevice',0x108:'kVarType_PrivateDriver',
          0x500:'kVarType_OmronPLC',0x501:'kVarType_ModBus_TCP',0x1000:'kVarType_ErrorHandler',0x1001:'kVarType_SafetyProtec'}