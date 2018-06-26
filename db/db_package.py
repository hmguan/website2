
from db import session_obj,user_info,package_info
from sqlalchemy import or_

class package_manager():
    def __init__(self):
        pass

    #返回该记录id
    @staticmethod
    def upload(user_id,package_name,version,time,remark):
        tmp = session_obj.query(user_info).filter_by(id=user_id).first()
        if(tmp ==None):
            return -1
        
        package_obj = package_info(user_id = user_id,package_name= package_name,version=version,time=time,remarks=remark)
        session_obj.add(package_obj)
        session_obj.commit()
        return package_obj.id

    @staticmethod
    def update(package_id,remark):
        tmp = session_obj.query(package_info).filter_by(id=package_id).first()
        if tmp ==None:
            return -1
        tmp.remarks = remark
        session_obj.commit()
        return 0

    @staticmethod
    def packages(user_id):
        return session_obj.query(package_info).filter(or_(user_id==user_id,user_id==1)).all()
    
    @staticmethod
    def remove(package_id):
        ret = session_obj.query(package_info).filter_by(id=package_id).first()
        if not ret:
            return -1

        tmp  = session_obj.query(package_info).get(ret.id)
        session_obj.delete(tmp)
        session_obj.commit()
        return 0
    
    