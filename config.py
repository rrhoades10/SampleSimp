import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_ENV = os.getenv('FLASK_ENV')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_ADMIN = os.getenv('MAIL_ADMIN')    
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    ALLOWED_IMAGE_EXTENSIONS = os.getenv('ALLOWED_IMAGE_EXTENSIONS')
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')
    POSTS_PER_PAGE = os.getenv('POSTS_PER_PAGE')
    # BASE_PATH = os.getenv('BASE_PATH')
    IMAGE_UPLOADS = os.getenv('IMAGE_UPLOADS')
    MAX_IMAGE_FILESIZE = os.getenv('MAX_IMAGE_FILESIZE')
    CLIENT_IMAGES = os.getenv('CLIENT_IMAGES')
    CLIENT_OTHER = os.getenv('CLIENT_OTHER')
    
    