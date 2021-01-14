from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from tape_app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'bp_users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from tape_app.bp_errors.handlers import bp_errors
    from tape_app.bp_main.routes import bp_main
    from tape_app.bp_admin.routes import bp_admin
    from tape_app.bp_posts.routes import bp_posts
    from tape_app.bp_users.routes import bp_users

    app.register_blueprint(bp_errors)
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_posts)
    app.register_blueprint(bp_users)

    return app
