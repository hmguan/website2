from flask import Flask
from flask_cors import CORS
from configuration import config_setting
from werkzeug.utils import secure_filename

def create_app(config_name):
    '''
    create flask application instance,
    and init all modules,regist the main blueprint
    :param config_name:the configuration name
    :return:the application instance object.
    '''
    app = Flask(__name__,static_url_path='',static_folder='web', template_folder='web')
    CORS(app, supports_credentials=True)
    app.config.from_object(config_setting[config_name])
    config_setting[config_name].init_app(app)

    #首先加载各子模块
    from .user import userflask
    from .shell import shell_flask
    from .mt import mtflask
    from .package import packageflask
    # from .blackbox import logview
    from .backup import backupview
    from .log_browser import logger_flask
    #加载主蓝图
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

def create_http_app(config_name)->Flask:
    '''
    create http application for handler long time event,
    this network communication user http protocal.
    :param config_name: the configuration name
    :return: the application instance object
    '''
    upapp = Flask(__name__,static_url_path='',static_folder='web', template_folder='web')
    CORS(upapp, supports_credentials=True)
    upapp.config.from_object(config_setting[config_name])
    config_setting[config_name].init_app(upapp)

    #加载http链接蓝图
    from .http import http_main as http_blueprint
    upapp.register_blueprint(http_blueprint)

    return upapp