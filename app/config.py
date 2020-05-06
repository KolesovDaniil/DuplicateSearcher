""""""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """"""

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_VALIDATE = True
    ERROR_404_HELP = False
