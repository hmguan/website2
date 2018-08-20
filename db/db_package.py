
from db import Session,user_info,package_info
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy.orm import subqueryload
from configuration import config
import os
from pynsp.logger import*
from agvshell.shell_api import is_file_open,is_package_in_task
class package_manager():
    def __init__(self):
        pass

    #返回该记录id
    @staticmethod
    def upload(user_id,package_name,version,time,remark):
        try:
            session_obj = Session()
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if(tmp ==None):
                Session.remove()
                return -1

            tmp = session_obj.query(package_info).options(subqueryload(package_info.user)).filter_by(package_name= package_name).filter_by(user_id = user_id).first()
            if tmp is not None:
                tmp  = session_obj.query(package_info).get(tmp.id)
                session_obj.delete(tmp)
                session_obj.commit()
                
            
            package_obj = package_info(user_id = user_id,package_name= package_name,version=version,time=time,remarks=remark)
            session_obj.add(package_obj)
            session_obj.commit()
            Session.remove()

            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -2 

    @staticmethod
    def update(package_id,remark):
        try:
            session_obj = Session()
            tmp = session_obj.query(package_info).filter_by(id=package_id).first()
            if tmp ==None:
                Session.remove()
                return -1
            tmp.remarks = remark
            session_obj.commit()
            Session.remove()
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -2 

    @staticmethod
    def packages(user_id):
        try:
            session_obj = Session()
            ret = session_obj.query(package_info).options(subqueryload(package_info.user)).filter(or_(package_info.user_id==user_id,package_info.user_id==1)).order_by(desc(package_info.user_id),desc(package_info.time)).all()
            Session.remove()
            return ret
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -2 
        
    @staticmethod
    def remove(package_id):
        try:
            session_obj = Session()
            ret = session_obj.query(package_info).filter_by(id=package_id).first()
            if not ret:
                Session.remove()
                return -1

            tmp  = session_obj.query(package_info).get(ret.id)
            folder_path = config.ROOTDIR +tmp.user.username +config.PATCHFOLDER
                        
            file_path = os.path.join(folder_path,tmp.package_name)

            if is_file_open(file_path) or is_package_in_task(package_id):
                Session.remove()
                return -4
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    Logger().get_logger().error(str(e))
                    session_obj.rollback() 
                    Session.remove()
                    return -2

            session_obj.delete(tmp)
            session_obj.commit()
            Session.remove()
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -3
        
    @staticmethod
    def query_packages(package_id):
        try:
            session_obj = Session()
            ret = session_obj.query(package_info).options(subqueryload(package_info.user)).filter_by(id=package_id).first()
            Session.remove()
            return ret
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -1
    
    
    
