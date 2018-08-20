
from db import Session,user_info,blackbox_temps
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
import os
from datetime import datetime
from pynsp.logger import*


class blackbox_manager():
    def __init__(self):
        pass
    
    @staticmethod
    def insert_temps(user_id,name,temps_types,others):
        try:
            session_obj = Session()
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if(tmp ==None):
                Session.remove()
                return -1
            
            temps_obj = blackbox_temps(user_id = user_id,name=name,temps_types= temps_types,others=others,time=datetime.datetime.now())
            session_obj.add(temps_obj)
            session_obj.commit()
            Session.remove()
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -2


    @staticmethod
    def temps(user_id):
        try:
            session_obj = Session()
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if(tmp ==None):
                Session.remove()
                return -1
            
            ret = session_obj.query(blackbox_temps).filter_by(user_id=user_id).order_by(desc(blackbox_temps.time)).all()
            Session.remove()
            return ret
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -2
    

    @staticmethod
    def remove_temps(temps_id):
        try:
            session_obj = Session()
            ret = session_obj.query(blackbox_temps).filter_by(id=temps_id).first()
            if not ret:
                Session.remove()
                return -1

            tmp  = session_obj.query(blackbox_temps).get(ret.id)

            session_obj.delete(tmp)
            session_obj.commit()
            Session.remove()
            return 0
        except Exception as e:
            Logger().get_logger().error(str(e))
            session_obj.rollback() 
            return -2
    
