from pynsp.loggercfg import init_loggercfg,LOG
import errtypes

LOG_INFO=1
LOG_DEBUG=2
LOG_WARNING=3
LOG_ERROR=4
LOG_FATAL=5

def init_logger():
    init_loggercfg('browser_logger')

def write_browser_logger(data):
    if data is None:
        LOG('browser_logger').error('the browser input log data is null')
        return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}

    log_type = data.get('type')
    if LOG_INFO == log_type:
        LOG('browser_logger').info('user_id:{0}, msg:{1}'.format(data.get('login_id'),data.get('msg')))
    elif LOG_DEBUG == data.get('type'):
        LOG('browser_logger').debug('user_id:{0}, msg:{1}'.format(data.get('login_id'),data.get('msg')))
    elif LOG_WARNING == data.get('type'):
        LOG('browser_logger').warning('user_id:{0}, msg:{1}'.format(data.get('login_id'),data.get('msg')))
    elif LOG_ERROR == data.get('type'):
        LOG('browser_logger').error('user_id:{0}, msg:{1}'.format(data.get('login_id'),data.get('msg')))
    elif LOG_FATAL == data.get('type'):
        LOG('browser_logger').fatal('user_id:{0}, msg:{1}'.format(data.get('login_id'),data.get('msg')))

    return {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal}