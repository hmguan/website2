from db import Session,user_info,file_list
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
import os
import datetime
from pynsp.logger import*
from configuration import config

class file_manager():
    def __init__(self):
        pass

    @staticmethod
    def insert(user_id,file_name,file_size):
        try:
            session_obj = Session()
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if(tmp ==None):
                Session.remove()
                return -1
            
            tmp = session_obj.query(file_list).filter_by(user_id=user_id).filter_by(file_name=file_name).first()
            if(tmp !=None):
                Session.remove()
                return -2
            time = datetime.datetime.now()
            list_obj = file_list(user_id = user_id,file_name= file_name,file_size =file_size,time=time)
            session_obj.add(list_obj)
            session_obj.commit()
            Session.remove()

            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -3  
        
    
    @staticmethod
    def file_list(user_id):
        try:
            session_obj = Session()
            now_t = datetime.date.today()- datetime.timedelta(days=15)
            file_manager.remove_by_day(datetime.datetime(now_t.year, now_t.month, now_t.day, datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second, 0))
            ret  = session_obj.query(file_list).filter_by(user_id=user_id).order_by(desc(file_list.time)).all()
            Session.remove()
            return ret
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -1 

    @staticmethod
    def remove(file_id):
        try:
            session_obj = Session()
            ret = session_obj.query(file_list).filter_by(id=file_id).first()
            if not ret:
                Session.remove()
                return -1

            tmp  = session_obj.query(file_list).get(ret.id)
            folder_path = config.ROOTDIR +tmp.user.username +config.BLACKBOXFOLDER
                        
            file_path = os.path.join(folder_path,tmp.file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    Session.remove()
                    Logger().get_logger().error(str(e))
                    return -2

            session_obj.delete(tmp)
            session_obj.commit()
            Session.remove()
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2


    @staticmethod
    def remove_by_day(to_day):
        try:
            session_obj = Session()
            session_obj.query(file_list).filter(file_list.time < to_day).delete()
            Session.remove()
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            return -2

        