#-*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    FLASKY_POSTS_PER_PAGE = 10

    SECRET_KEY = os.getenv('SECRET_KEY') or 'hard to guess string'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # IMM账号配置
    ACCESS_KEY_ID = 'LTAIIXP5r3gpP5ZM'
    ACCESS_KEY_SECRET = 'wXbYInlyUnqc5p7H338u9fpog1sqCf'
    IMM_REGION = 'cn-beijing'

    # OSS相关配置
    OSS_TEST_ACCESS_ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
    OSS_TEST_ACCESS_BUCKET = 'co-user-cn-beijing'
    OSS_TEST_ACCESS_PREFIX = 'zqh/input/FaceGroup/'


    # INDEXFACEx相关配置
    FACE_PROJECT = 'img-face-server-co-beijing'
    FACE_SET_ID = 'FACE-4c3b76fe-dd8c-4e48-b4be-14643f024978'

    ALLOWED_EXTENSIONS = set(['bmp', 'png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF'])


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:aa123456@127.0.0.1/db_remark?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URL') or 'mysql+pymysql://root:AIMarker@DB@rm-uf6f84tgdv6ti66ah.mysql.rds.aliyuncs.com/db_marker?charset=utf8'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}



