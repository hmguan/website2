

from db import session_obj,user_info,group_alias_info
from pynsp.logger import*

class user:
    def __init__(self):
        pass
    
    @staticmethod
    def is_exist(username)->int:
        ret = session_obj.query(user_info).filter_by(username=username).first()
        if(ret ==None):
            return -1
        return 0
        
    @staticmethod
    def is_exist_id(user_id)->int:
        try:
            ret = session_obj.query(user_info).filter_by(id=user_id).first()
            if(ret ==None):
                return -1
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2

    #用户校验 
    @staticmethod
    def verification(username,pwd)->tuple:
        try:
            tmp = session_obj.query(user_info).filter_by(username=username).filter_by(pwd=pwd).first()
            if(tmp ==None):
                return -1,-1
            if 'guest'== tmp.identity_type:
                user_type = 0
            else:
                user_type = 1
            return tmp.id,user_type
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2,-2

    #添加用户
    @staticmethod
    def append(username,pwd,permission,identity_type='guest')->int:
        try:
            if user.is_exist(username)>=0:
                return -1
            user_obj = user_info(username=username,pwd=pwd,identity_type=identity_type,user_path='/',permission = permission)
            session_obj.add(user_obj)
            session_obj.commit()
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2
        return 0

    #更新密码
    @staticmethod
    def update_pwd(user_id,pwd,new_pwd)->int:
        try:
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if tmp ==None:
                return -1
            if tmp.pwd !=pwd:
                return -2
            tmp.pwd = new_pwd
            session_obj.commit()
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -3
        return 0

    #重置密码
    @staticmethod
    def reset_pwd(user_id)->int:
        try:
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if tmp ==None:
                return -1
            tmp.pwd = "e10adc3949ba59abbe56e057f20f883e"
            session_obj.commit()
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2
       
        return 0

    @staticmethod
    def reset_permission(user_id,permission):
        try:
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if tmp ==None:
                return -1
            tmp.permission = permission
            session_obj.commit()
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2
        return 0

    #删除用户
    @staticmethod
    def remove(user_id)->int:
        try:
            ret = session_obj.query(user_info).filter_by(id=user_id).first()
            if not ret:
                return -1
        
            #删除用户
            tmp = session_obj.query(user_info).get(ret.id)
            session_obj.delete(tmp)
            session_obj.commit()
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2
        return 0

    #通过id 查询用户名
    @staticmethod
    def query_name_by_id(user_id)->tuple:
        try:
            ret = session_obj.query(user_info).filter_by(id=user_id).first()
            if not ret:
                return (-1,'')
            return (0,ret.username)
        except Exception as e:
            Logger().get_logger().error(str(e))
            return (-2,'')

    #查询用户
    @staticmethod
    def users():
        try:
            return (0,session_obj.query(user_info).all())
        except Exception as e:
            Logger().get_logger().error(str(e))
            return (-1,[])
        

    #查询组别名
    @staticmethod
    def group_alias(login_id,group_name):
        try:
            ret = session_obj.query(user_info).filter_by(id=login_id).first()
            if not ret:
                return (-1,'')
            
            ret = session_obj.query(group_alias_info).filter_by(user_id=login_id).filter_by(name=group_name).first()
            if ret is None:
                alias_obj = group_alias_info(user_id = login_id,name=group_name)
                session_obj.add(alias_obj)
                session_obj.commit()
                return (0,'')
            return (0,ret.alias)
        
        except Exception as e:
            Logger().get_logger().error(str(e))
            return (-2,'')


    #更新查询组别名
    @staticmethod
    def update_group_alias(login_id,group_name,alias):
        try:
            ret = session_obj.query(user_info).filter_by(id=login_id).first()
            if not ret:
                return -1
            
            ret = session_obj.query(group_alias_info).filter_by(user_id=login_id).filter_by(name=group_name).first()
            if not ret:
                return -2
            ret.alias = alias
            session_obj.commit()
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -3
        return 0


    



    

   
