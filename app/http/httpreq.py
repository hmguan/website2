import urllib3
import requests
import json
from configuration import config

#  忽略警告：InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised.
requests.packages.urllib3.disable_warnings()
# 一个PoolManager实例来生成请求, 由该实例对象处理与线程池的连接以及线程安全的所有细节
http = urllib3.PoolManager()

def http_post(url,data_json):
    jdata = json.dumps(data_json)
    req=http.request('POST',
                     url,
                     body=jdata,
                     headers={'Content-Type':'application/json'},timeout=3.0)
    return req.data.decode('utf-8')

def get_user_id(login_token)->json:
    try:
        web_port = config.WEB_PORT
    except Exception as e:
        web_port = 5008
    url='http://localhost:{0}/'.format(web_port)
    data_json={'event':'event_get_userid','login_token':login_token}
    response = http_post(url,data_json)
    return json.loads(response)
