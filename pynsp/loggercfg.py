import logging.config
import os
import datetime
import pynsp.singleton as slt

def init_logger(file_name):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # 创建路径

    LOG_FILE = file_name + datetime.datetime.now().strftime("%Y%m%d%H%m%s") + ".log"

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%Y-%m-%d %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {'filter_by_name': {'class': 'logging.Filter',
                                        'name': file_name},
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                # 当达到10MB时分割日志
                'maxBytes': 1024 * 1024 * 10,
                # 最多保留1024份文件
                'backupCount': 1024,
                # If delay is true,
                # then file opening is deferred until the first call to emit().
                'delay': True,
                'filename': os.path.join(LOG_DIR, LOG_FILE),
                'formatter': 'verbose'
            }
        },
        'loggers': {
            file_name: {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate':False,
            },
        }
    })

logger_handler_list = {}

def init_loggercfg(file_name):
    init_logger(file_name)
    logger = logging.getLogger(file_name)
    logger_handler_list[file_name] = logger

def LOG(file_name):
    handler = logger_handler_list.get(file_name)
    if handler is not None:
        return handler

if __name__ == '__main__':
    pass