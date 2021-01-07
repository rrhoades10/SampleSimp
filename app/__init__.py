from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail
from elasticsearch import Elasticsearch
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'authentication.login'
login.login_message = 'You do not have to access to this page.'
login.login_message_category = 'danger'

moment = Moment()
mail = Mail()

# def allowedfiles(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .blueprints.blog import bp as blog_bp
    app.register_blueprint(blog_bp)

    from .blueprints.authentication import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app