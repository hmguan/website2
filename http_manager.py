from app import create_http_app
from configuration import config

upload_app = create_http_app('default')

if __name__ == '__main__':
    try:
        http_port = config.HTTP_PORT
        upload_app.run(host='0.0.0.0', port=http_port, debug=True,use_reloader=False)
    except Exception as e:
        print('Bound port failure')
