from app import create_http_app

upload_app = create_http_app('default')

if __name__ == '__main__':
    upload_app.run(host='0.0.0.0', port=5010, debug=True,use_reloader=False)