import logging.config
import os
import datetime
import pynsp.singleton as slt

def init_logger():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # 创建路径

    LOG_FILE = 'website_' + datetime.datetime.now().strftime("%Y%m%d%H%m%s") + ".log"

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%Y-%m-%d %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
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
            '': {
                'handlers': ['file','console'],
                'level': 'DEBUG',
            },
        }
    })

init_logger()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('log info')