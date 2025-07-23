from dotenv import load_dotenv
import os

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    POSTS_PER_PAGE = 3
    LANGUAGES = ['en']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    MS_TRANSLATOR_REGION = os.environ.get('MS_TRANSLATOR_REGION')

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    # # 🔽 New lines for file upload support
    # UPLOAD_FOLDER = os.path.join(basedir, 'app/static/profile_pics')
    # MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB limit
    # ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
