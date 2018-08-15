from db.db_users import user
from threading import Thread,RLock
import errtypes
from app.soketio import socketio_agent_center 
from app.user.user_cls import user_cls
from pynsp.singleton import singleton
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from configuration import config
import uuid
from db.db_logger import logger_manager
from datetime import datetime
import copy


ROOT_ID = 1
@singleton
class user_manager():
    def __init__(self):
        self.login_user_ = {}
        self.login_mutex_ = RLock()

    #添加用户
    def register_user(self,login_id,user_name,pwd,permission):
        if ROOT_ID!=login_id:
             return {'code':errtypes.HttpResponseCode_PermissionDenied,'msg':errtypes.HttpResponseCodeMsg_PermissionDenied}
        ret = user.append(user_name,pwd,permission)
        if (-1==ret):
            return {'code':errtypes.HttpResponseCode_UserExisted,'msg':errtypes.HttpResponseCodeMsg_UserExisted}
        if (-2==ret):
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}
        return {'code':0,'msg':'success'}

    #删除用户
    def remove_user(self,login_id,target_id):
        if ROOT_ID!=login_id:
             return {'code':errtypes.HttpResponseCode_PermissionDenied,'msg':errtypes.HttpResponseCodeMsg_PermissionDenied}
        ret = user.remove(target_id)
        if (-1==ret):
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted}
        if (-2==ret):
            return {'code':errtypes.HttpResponseCode_ServerError,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}

        self.login_mutex_.acquire()
        u_uuid=''
        if target_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[target_id].u_uuid)
            del self.login_user_[target_id]
            msg = "该账号信息已被修改，请重新登录！"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_RootOper,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
            logger_manager.insert(user_id = target_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()

        msg = "删除成功"
        #logger_manager.insert(user_id = target_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':'success'}


    #更新密码
    def update_pwd(self,login_id,pwd,new_pwd):
        ret = user.update_pwd(login_id,pwd,new_pwd)
        if (-1==ret):
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted}
        if (-2==ret):
            return {'code':errtypes.HttpResponseCode_InvaildUserOrPwd,'msg':errtypes.HttpResponseCodeMsg_InvaildUserOrPwd}
        if (-3==ret):
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}

        self.login_mutex_.acquire()
        u_uuid=''
        if login_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[login_id].u_uuid)
            del self.login_user_[login_id]
            msg = "更新密码成功，请重新登录！"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UpdatePWD,'uuid':u_uuid},room_identify=u_uuid)
            #logger_manager.insert(user_id = login_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()
        

        msg = "更新密码成功，请重新登录！"
        logger_manager.insert(user_id = login_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':'success'}


    #重置密码
    def reset_pwd(self,login_id,target_id):
        if ROOT_ID!=login_id:
            return {'code':errtypes.HttpResponseCode_PermissionDenied,'msg':errtypes.HttpResponseCodeMsg_PermissionDenied}
        ret = user.reset_pwd(target_id)
        if (-1==ret):
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted}
        if (-2==ret):
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}

        self.login_mutex_.acquire()
        u_uuid=''
        if target_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[target_id].u_uuid)
            del self.login_user_[target_id]
            msg = "该账号信息已被修改，请重新登录！"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_RootOper,'uuid':u_uuid},room_identify=u_uuid)
            #logger_manager.insert(user_id = target_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()

        msg = "账号信息已被修改"
        logger_manager.insert(user_id = target_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':'success'}

    
    #重置权限
    def reset_permission(self,login_id,target_id,permission):
        if ROOT_ID!=login_id:
            return {'code':errtypes.HttpResponseCode_PermissionDenied,'msg':errtypes.HttpResponseCodeMsg_PermissionDenied}

        ret = user.reset_permission(target_id,permission)
        if (-1==ret):
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted}
        if (-2==ret):
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}
        
        self.login_mutex_.acquire()
        u_uuid=''
        if target_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[target_id].u_uuid)
            del self.login_user_[target_id]
            msg = "该账号信息已被修改，请重新登录！"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_RootOper,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
            #logger_manager.insert(user_id = target_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()

        msg = "修改权限成功"
        logger_manager.insert(user_id = target_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':'success'}


    #查询用户
    def users(self,login_id):
        if ROOT_ID!=login_id:
            return {'code':errtypes.HttpResponseCode_PermissionDenied,'msg':errtypes.HttpResponseCodeMsg_PermissionDenied}
        
        (ret,user_list) = user.users()
        if -1==ret:
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}
        
        dict_users=[]
        for index, value in enumerate(user_list):
            dict_user={}
            if 'root'==value.username:
                continue
            dict_user['target_id'] = value.id
            dict_user['user_name']= value.username
            dict_user['permission'] = value.permission
            dict_users.append(dict_user)
        return {'code':0,'msg':'success','data':{'users':dict_users}}


    #返回tuple(retval,login_id)  
    #### retval:错误码   
    #### login_id：当retval=0有效
    def check_user_login(self,token)->tuple:
        s = Serializer(config.SECRET_KEY)
        user_id = 0
        try:
            data = s.loads(token)
            user_id = data['id']
            ret_id  =  user.is_exist_id(user_id)
            if -1==ret_id:
                return (errtypes.HttpResponseCode_UserNotExisted,-1)
            if -2==ret_id:
                return (errtypes.HttpResponseCode_Sqlerror,-1)
        except SignatureExpired:
            msg = "登录信息已过期，请重新登录！"
            return (errtypes.HttpResponseCode_TimeoutToken,-1)
        except BadSignature:
            msg = "登录信息有误，请重新登录！"
            return (errtypes.HttpResponseCode_InvaildToken,-1)
        return (0,user_id)

    def check_user_token(self,token):
        s = Serializer(config.SECRET_KEY)
        
        data = s.loads(token)
        return data['id']

    def find_token_by_userid(self,user_id):
        self.login_mutex_.acquire()
        token=''
        if user_id in self.login_user_.keys():
            token = self.login_user_[user_id].token
        self.login_mutex_.release()
        return token

    #生成密钥
    def generate_auth_token(self, id,expiration = 86400):
        s = Serializer(config.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': id })
    
    def verify_auth_token(self,token,user_uuid):
        # step 1: 验证token
        s = Serializer(config.SECRET_KEY)
        user_id = 0
        try:
            data = s.loads(token)
            user_id = data['id']
            ret_id  = user.is_exist_id(user_id)
            if -1==ret_id:
                return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted,'data':{'token':token}} 
            if -2==ret_id:
                return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror,'data':{'token':token}}
            
        except SignatureExpired:
            msg = "登录信息已过期，请重新登录！"
            logger_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid=user_uuid)
            return {'code':errtypes.HttpResponseCode_TimeoutToken,'msg':errtypes.HttpResponseCodeMsg_TimeoutToken,'data':{'token':token}} 
        except BadSignature:
            msg = "登录信息有误，请重新登录！"
            logger_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid=user_uuid)
            return {'code':errtypes.HttpResponseCode_InvaildToken,'msg':errtypes.HttpResponseCodeMsg_InvaildToken,'data':{'token':token}} 

        # step 2 检查踢人
        self.login_mutex_.acquire()
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
            if user_uuid != u_uuid:
                msg = "该用户已在另一地点登录，请重新登录！"
                socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UserOffline,'uuid': u_uuid},room_identify=u_uuid)
                logger_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
            self.login_user_[user_id].u_uuid = user_uuid

        else:
            user_obj = user_cls('','')
            user_obj.user_id = user_id
            user_obj.u_uuid = user_uuid
            user_obj.token = token
            self.login_user_[user_id] = user_obj
        

        self.login_mutex_.release()

        #logger_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg="登录成功token",u_uuid=user_uuid)
        return {'code':0,'msg':'success','data':{'login_token':token,'uuid':u_uuid}}


    #用户登录
    def user_login(self,user_name=None,pwd=None)->dict:
        

        #step 1: 验证登录有效性
        self.login_mutex_.acquire()
        user_obj = user_cls(user_name,pwd)
        user_id = user_obj.login()
        if -1==user_id:
            self.login_mutex_.release()
            msg = "密码错误"
            #logger_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid='123')
            return {'code':errtypes.HttpResponseCode_InvaildUserOrPwd,'msg':errtypes.HttpResponseCodeMsg_InvaildUserOrPwd}
        if -2==user_id:
            self.login_mutex_.release()
            msg = "sql error"
            #logger_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid='123')
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}
        #step 2: 检查踢人
        if user_id in self.login_user_.keys():
            tmp = self.login_user_[user_id].u_uuid
            msg = "该用户已在另一地点登录，请重新登录！"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UserOffline,'uuid':tmp},room_identify=tmp)
            #logger_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=tmp)
       
        #step 3：更新用户uuid
        new_uuid = uuid.uuid4().__str__()
        user_obj.u_uuid = new_uuid
        token = self.generate_auth_token(user_id)
        user_obj.token = token

        self.login_user_[user_id] = user_obj

        self.login_mutex_.release()
       
       
        msg = "登录成功"
        #logger_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid=new_uuid)
        return {'code':0,'msg':'success','data':{'uuid':new_uuid,'login_token':token.decode('utf-8')}}


    #注销登录
    def user_logout(self,login_id)->dict:
        self.login_mutex_.acquire()
        u_uuid=''
        if login_id not in self.login_user_.keys():
            msg = "用户未登录"
            logger_manager.insert(user_id = login_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid="")
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_UserNotLogin,'msg':errtypes.HttpResponseCodeMsg_UserExisted}
        
        u_uuid = copy.deepcopy(self.login_user_[login_id].u_uuid)
        del self.login_user_[login_id]
        self.login_mutex_.release()


        msg = "注销登录，通知用户下线"
        socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_Loginout,'uuid':u_uuid},room_identify=u_uuid)
        #logger_manager.insert(user_id = login_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)

        return {'code':0,'msg':'success'}

    #查询用户uuid
    def user_uuid(self,user_id):
        self.login_mutex_.acquire()
        u_uuid=''
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
        self.login_mutex_.release()
        return u_uuid

    
    ################################ 组别名##############################
    #查询别名
    def group_alias(self,login_id,group_name):
        (ret,alias)= user.group_alias(login_id,group_name)
        if -1==ret:
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted}
        if -2==ret:
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}
        
        if None == ret:
            return {'code':0,'msg':'success','alias':''}
        return {'code':0,'msg':'success','alias':alias}
        

    #更新组名
    def update_group_alias(self,login_id,group_name,alias):
        ret = user.update_group_alias(login_id,group_name,alias)
        if -1==ret:
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':errtypes.HttpResponseCodeMsg_UserNotExisted}
        if -2==ret:
            return {'code':errtypes.HttpResponseCode_InvaildGroup_Name}
        if -3==ret:
            return {'code':errtypes.HttpResponseCode_Sqlerror,'msg':errtypes.HttpResponseCodeMsg_Sqlerror}
        return {'code':0,'msg':'success'}

   
    
