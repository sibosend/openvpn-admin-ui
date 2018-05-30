# all the imports
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_ldap_login import LDAPLoginManager
import os

app = Flask(__name__)

deploy_env = os.environ.get('DEPLOY_TARGET', 'default');
app.config.from_object("config." + deploy_env.capitalize() + 'Config')

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment()
db = SQLAlchemy()
mail = Mail()

login_manager = LoginManager()
#login_manager.init_app(app)
ldap_mgr = LDAPLoginManager(app)

from firstApp.views import firstApp_app
app.register_blueprint(firstApp_app)
from firstApp import models

def create_app():
    db.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    return app
