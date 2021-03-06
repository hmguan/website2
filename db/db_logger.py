from db import Session,logger,user_info

class logger_manager():
    def __init__(self):
        pass

    #返回该记录id
    @staticmethod
    def insert(user_id,login_type,time,msg,u_uuid,remark=''):
        session_obj = Session()
        tmp = session_obj.query(user_info).filter_by(id=user_id).first()
        if(tmp ==None):
            Session.remove()
            return -1

        package_obj = logger(user_id = user_id,login_type= login_type,time =time,msg=msg,u_uuid=u_uuid,remarks = remark )
        session_obj.add(package_obj)
        session_obj.commit()
        Session.remove()
        return 0