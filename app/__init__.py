# -*- coding: utf-8 -*-
__author__ = "Boris Drozdovski, TLV"
__version__ = "0.98"

from flask import Flask
from flask_login import LoginManager
from flask_compress import Compress
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import logging
from logging.handlers import SysLogHandler

from app.utils import timestamp_to_date, format_memory, format_date
from config import *
# from flask_sslify import SSLify


def version():
    if os.getenv("APP_BUILD_VERSION"):
        return os.getenv("APP_BUILD_VERSION")
    else:
        return 'local'


ver = f'{__version__}.{version()}'


# basedir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(basedir, 'instance')
mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()
login = LoginManager()
# login.session_protection = 'basic'
login.login_view = 'login'


def create_app():
    app = Flask(__name__)
    app.secret_key = 'uyTbf8AEtYjV3N6H48m6Z2vS3KjcEdXH'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, cfg["sqlite_db_name"])
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(Config)

    mail.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    login.init_app(app)

    if os.environ.get('FLASK_ENV') == 'production':  # Log to syslog
        # SSLify(app)  # Configure SSL if platform supports it
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

    # TODO here!
    # Register Jinja template functions
    app.add_template_filter(timestamp_to_date, 'timestamp2date')
    app.add_template_filter(format_memory, 'convert_mib')
    app.add_template_filter(format_date, 'date_format')

    # Create app blueprints
    from .views import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/users')

    from .views import general as general_blueprint
    app.register_blueprint(general_blueprint)

    from .views import servers as servers_blueprint
    app.register_blueprint(servers_blueprint, url_prefix='/servers')

    return app
