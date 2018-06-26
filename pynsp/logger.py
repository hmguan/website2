import logging
import logging.handlers
import sys
import os
import threading
import pynsp.singleton as slt
import datetime

#log levels
LOG_LEVEL_NOTSET=logging.NOTSET
LOG_LEVEL_DEBUG=logging.DEBUG
LOG_LEVEL_INFO=logging.INFO
LOG_LEVEL_WARNING=logging.WARNING
LOG_LEVEL_ERROR=logging.ERROR

#log output target
LOGGER_FORMAT= "[%(asctime)s] %(levelname)s [%(thread)x] [%(module)s:%(lineno)s] %(message)s" #"[%(levelname)7s] [%(asctime)s] [%(thread)d] [%(module)s] -%(message)s"

#生成处理器
class HandlerFactory(object):
    handlers = {}

    @classmethod
    def get_std_out_handler(cls):
        if 'std_out_handler' not in cls.handlers:
            std_out_handler = logging.StreamHandler(sys.stdout)
            #set logger formate
            std_out_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
            cls.handlers['std_out_handler']=std_out_handler

        return cls.handlers['std_out_handler']

    @classmethod
    def get_std_err_handler(cls):
        if 'std_err_handler' not in cls.handlers:
            std_err_handler=logging.StreamHandler(sys.stderr)
            #set logger formate
            std_err_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
            #set log level
            std_err_handler.setLevel(LOG_LEVEL_WARNING)
            cls.handlers['std_err_handler']=std_err_handler

        return cls.handlers['std_err_handler']

    @classmethod
    def get_rotating_file_handler(cls,log_path,max_bytes,backup_count):
        if 'rotating_file_handler' not in cls.handlers:
            cls.handlers['rotating_file_handler']={}

        if log_path not in cls.handlers['rotating_file_handler']:
            rotation_file_handler = logging.handlers.RotatingFileHandler(log_path, mode='a',
                                                                         maxBytes=max_bytes,
                                                                         backupCount=backup_count,
                                                                         encoding='utf-8')
            rotation_file_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
            cls.handlers['rotating_file_handler'][log_path]=rotation_file_handler

        return cls.handlers['rotating_file_handler'][log_path]

#logger for this module ,return a logger instance，if not input name，return root logger

@slt.singleton
class Logger():
    def __init__(self,level=LOG_LEVEL_DEBUG,log_by_thread=False,log_path='',max_bytes=0,backup_count=0):
        #set root logger
        logging.getLogger().setLevel(LOG_LEVEL_NOTSET)
        logging.getLogger().addHandler(HandlerFactory.get_std_out_handler())
        logging.getLogger().addHandler(HandlerFactory.get_std_err_handler())

        #default logger setting
        self.__logger={}
        self.__log_level=level
        self.__main_thread_id=str(self.get_current_thread_id())
        self.__log_by_thread=log_by_thread
        self.__log_path=log_path
        self.__log_file_max_bytes=max_bytes
        self.__log_file_backup_count=backup_count

    @staticmethod
    def get_current_thread_id():
        return threading.current_thread().ident

    @staticmethod
    def get_current_thread_name():
        return threading.current_thread().name

    def get_log_file_name(self):
        log_path=os.path.abspath(self.__log_path)
        base_name=os.path.basename(log_path)
        base_dir=os.path.dirname(log_path)

        if self.__log_by_thread:
            base_name='%d_%s_%s' % (self.get_current_thread_id(),self.get_current_thread_name(),base_name)

        if os.path.isdir(log_path):
            #only folder path provided,create a name for the log file
            return os.path.join(log_path,base_name)
        elif base_name and '.' not in base_name:
            #create folder
            os.mkdir(base_name)
            return os.path.join(log_path,base_name)
        else:
            return os.path.join(base_dir,base_name)

    def get_logger(self)->logging.Logger:
        name=self.__main_thread_id

        if self.__log_by_thread:
            current_id=str(self.get_current_thread_id())

            if current_id != self.__main_thread_id:
                name = self.__main_thread_id+'.'+current_id

        if name not in self.__logger:
            self.set_logger(name)

        return self.__logger[name]

    def set_logger(self,name):
        if name not in self.__logger:
            new_logger=logging.getLogger(name)
            new_logger.setLevel(self.__log_level)

            if self.__log_path:
                log_path=self.get_log_file_name()
                new_logger.addHandler(HandlerFactory.get_rotating_file_handler(log_path,
                                                                               self.__log_file_max_bytes,
                                                                               self.__log_file_backup_count))
            self.__logger[name] = new_logger

    def set_log_path(self,file_path,max_bytes=0,backup_count=0):
        if isinstance(file_path,str):
            self.__log_path=file_path
        if isinstance(max_bytes,int):
            self.__log_file_max_bytes=max_bytes
        if isinstance(backup_count,int):
            self.__log_file_backup_count=backup_count

    def set_log_level(self,new_level):
        self.__log_level=new_level
        for instancelogger in self.__logger.values():
            instancelogger.setLevel(self.__log_level)

    def set_log_by_thread_log(self,log_by_thread):
        self.__log_by_thread=log_by_thread
        for instancelogger in self.__logger.values():
            instancelogger.disabled = not self.__log_by_thread

        try:
            self.__logger[self.__main_thread_id].disabled=self.__log_by_thread
        except KeyError:
            pass

def init_logger():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # 创建路径
    LOG_FILE = 'website_' + datetime.datetime.now().strftime("%Y%m%d%H%m%s") + ".log"
    Logger().set_log_path(os.path.join(LOG_DIR, LOG_FILE),max_bytes=1024*1024*10,backup_count=100)
    Logger().set_log_by_thread_log(False)
    Logger().set_log_level(LOG_LEVEL_DEBUG)