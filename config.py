import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    POSTS_PER_PAGE = 3
    LANGUAGES = ['en', 'es', 'bn']
# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'sqlite:///' + os.path.join(basedir, 'app.db')

#     MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
#     MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
#     MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
#     MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'apikey'   # your SendGrid username
#     MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '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'  # your SendGrid API key
#     MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'wassemrayhan02@gmail.com'
#     ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'asaduzzamanrayhan15@gmail.com'

#     POSTS_PER_PAGE = 3