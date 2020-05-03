""""""

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """"""

    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    RESTPLUS_MASK_SWAGGER = False
