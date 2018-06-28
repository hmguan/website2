
from db import session_obj,user_info,package_info
from sqlalchemy import or_
from configuration import config
import os


class package_manager():
    def __init__(self):
        pass

    #返回该记录id
    @staticmethod
    def upload(user_id,package_name,version,time,remark):
        tmp = session_obj.query(user_info).filter_by(id=user_id).first()
        if(tmp ==None):
            return -1

        tmp = session_obj.query(user_info).filter_by(package_name= package_name).first()
        if(tmp ==None):
            return -2
        
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
        return session_obj.query(package_info).filter(or_(package_info.user_id==user_id,package_info.user_id==1)).all()
    
    @staticmethod
    def remove(package_id):
        ret = session_obj.query(package_info).filter_by(id=package_id).first()
        if not ret:
            return -1

        tmp  = session_obj.query(package_info).get(ret.id)
        folder_path = config.ROOTDIR +tmp.user.username +config.PATCHFOLDER
                    
        file_path = os.path.join(folder_path,tmp.package_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        session_obj.delete(tmp)
        session_obj.commit()
        return 0

    @staticmethod
    def query_packages(package_id):
        return session_obj.query(package_info).filter_by(id=package_id).first()

    
    
    
