from db.db_users import user
from threading import Thread,RLock
import errtypes
from app.soketio import socketio_agent_center 
from app.user.user_cls import user_cls
from pynsp.singleton import singleton
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from configuration import config
import uuid
from db.db_logger import login_manager
from datetime import datetime
import copy

@singleton
class user_manager():
    def __init__(self):
        self.login_user_ = {}
        self.login_mutex_ = RLock()

    #生成密钥
    def generate_auth_token(self, id,expiration = 2592000):
        s = Serializer(config.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': id })
    
    def verify_auth_token(self,token,user_uuid):
        # step 1: 验证token
        s = Serializer(config.SECRET_KEY)
        try:
            data = s.loads(token)
            user_id = data['id']
        except SignatureExpired:
            msg = "登陆信息已过期，请重新登陆！"
            login_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid=user_uuid)
            return {'code':errtypes.HttpResponseCode_TimeoutToken,'msg':msg,'data':{'token':token}} 
        except BadSignature:
            msg = "登陆信息有误，请重新登陆！"
            login_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid=user_uuid)
            return {'code':errtypes.HttpResponseCode_InvaildToken,'msg':msg,'data':{'token':token}} 

        # step 2 检查踢人
        self.login_mutex_.acquire()
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
            if user_uuid != u_uuid:
                msg = "通知用户下线（token）"
                socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid': u_uuid},room_identify=u_uuid)
                login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
            self.login_user_[user_id].u_uuid = user_uuid

        else:
            user_obj = user_cls('','')
            user_obj.user_id = user_id
            user_obj.u_uuid = user_uuid
            self.login_user_[user_id] = user_obj
        

        self.login_mutex_.release()

        login_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg="登陆成功token",u_uuid=user_uuid)
        return {'code':0,'msg':'登陆成功','data':{'token':token,'user_id':user_id}}


    #添加用户
    def register_user(self,user_name,pwd,permission):
        ret = user.append(user_name,pwd,permission)
        if (ret<0):
            return {'code':errtypes.HttpResponseCode_UserExisted,'msg':'该用户已存在'}
        return {'code':ret,'msg':'添加成功'}

    #用户登录
    def user_login(self,user_name=None,pwd=None)->dict:
        ret = user.query_userid_by_name(user_name)
        if(ret<0):
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':'用户不存在'}

        #step 1: 验证登陆有效性
        self.login_mutex_.acquire()
        user_obj = user_cls(user_name,pwd)
        user_id = user_obj.login()
        if user_id < 0:
            self.login_mutex_.release()
            msg = "密码错误"
            login_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid='')
            return {'code':errtypes.HttpResponseCode_InvaildUserAndPwd,'msg':msg}
       
        #step 2: 检查踢人
        if user_id in self.login_user_.keys():
            tmp = self.login_user_[user_id].u_uuid
            msg = "通知用户下线"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid':tmp},room_identify=tmp)
            login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=tmp)
       
        #step 3：更新用户uuid
        new_uuid = uuid.uuid4().__str__()
        user_obj.u_uuid = new_uuid
        self.login_user_[user_id] = user_obj

        self.login_mutex_.release()
        
        #step 4：生成token
        token = self.generate_auth_token(user_id)

        msg = "登陆成功"
        login_manager.insert(user_id = user_id,login_type='online',time =datetime.now(),msg=msg,u_uuid=new_uuid)
        return {'code':0,'msg':msg,'data':{'uuid':new_uuid,'token':token.decode('utf-8'),'user_id':user_id}}


    #注销登陆
    def user_logout(self,user_id)->dict:
        self.login_mutex_.acquire()
        u_uuid=''
        if user_id not in self.login_user_.keys():
            msg = "用户未登陆"
            login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid="")
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_UserNotLogined,'msg':msg}
        
        u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
        del self.login_user_[user_id]
        self.login_mutex_.release()


        msg = "注销登陆，通知用户下线"
        socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
        login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)

        return {'code':0,'msg':'注销成功'}

    #删除用户
    def remove_user(self,user_id):
        
        self.login_mutex_.acquire()
        ret = user.remove(user_id)
        if (ret<0):
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':'用户不存在'} # 正常情况不会出现

        u_uuid=''
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
            del self.login_user_[user_id]
            msg = "删除用户，通知用户下线"
            socketio_agent_center.post_msg_to_room({'code':errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
            login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()

        msg = "删除成功"
        login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':msg}

    #更新密码
    def update_pwd(self,user_id,pwd,new_pwd):

        self.login_mutex_.acquire()
        ret = user.update_pwd(user_id,pwd,new_pwd)
        if (ret==-1):
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':'用户不存在'}
        if (ret==-2):
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_InvaildUserAndPwd,'msg':'原密码不正确'}

        u_uuid=''
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
            del self.login_user_[user_id]
            msg = "更新密码，通知用户下线"
            socketio_agent_center.post_msg_to_room({'code':-errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
            login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()
        

        msg = "更新密码成功"
        login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':msg}

    #重置密码
    def reset_pwd(self,user_id):
        
        self.login_mutex_.acquire()
        ret = user.reset_pwd(user_id)
        if (ret==-1):
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':'用户不存在'}

        u_uuid=''
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
            del self.login_user_[user_id]
            msg = "重置密码，通知用户下线"
            socketio_agent_center.post_msg_to_room({'code':-errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
            login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()


        msg = "重置密码成功"
        login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':msg}

    #重置权限
    def reset_permission(self,user_id,permission):
    
        self.login_mutex_.acquire()
        ret = user.reset_permission(user_id,permission)
        if (ret==-1):
            self.login_mutex_.release()
            return {'code':errtypes.HttpResponseCode_UserNotExisted,'msg':'用户不存在'}
        
        u_uuid=''
        if user_id in self.login_user_.keys():
            u_uuid = copy.deepcopy(self.login_user_[user_id].u_uuid)
            del self.login_user_[user_id]
            msg = "重置权限，通知用户下线"
            socketio_agent_center.post_msg_to_room({'code':-errtypes.HttpResponseCode_UserOffline,'msg':msg,'uuid':u_uuid},room_identify=u_uuid)
            login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        self.login_mutex_.release()

        msg = "修改权限成功"
        login_manager.insert(user_id = user_id,login_type='offline',time =datetime.now(),msg=msg,u_uuid=u_uuid)
        return {'code':ret,'msg':msg}
    
    #查询用户
    def users(self):
        ret = user.users()
        dict_users=[]
        for index, value in enumerate(ret):
            dict_user={}
            if 'root'==value.username:
                continue
            dict_user['user_id'] = value.id
            dict_user['user_name']= value.username
            dict_user['permission'] = value.permission
            dict_users.append(dict_user)
        return {'code':0,'msg':'success','data':{'users':dict_users}}

    #查询别名
    def group_alias(self,user_id,group_name):
        return user.group_alias(user_id,group_name)

    #更新组名
    def update_group_alias(self,user_id,group_name,alias):
        ret = user.update_group_alias(user_id,group_name,alias)
        if ret<0:
            return {'code':errtypes.HttpResponseCode_InvaildGroup_Name,'msg':'更新失败'}
        return {'code':ret,'msg':'更新组名成功'}
    
