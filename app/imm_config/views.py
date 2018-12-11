# -*-coding: utf-8-*-
from . import imm_config
from flask import jsonify, current_app
from app.models import db, Config
from app.util.get_request_param import get_form_param
from app.util.aliyun_api import sent_request, Client
from app.util.custom_error import CustomFlaskErr
from aliyunsdkcore.profile.region_provider import add_endpoint
import httplib
import traceback


# 编辑配置
@imm_config.route('editConfig', methods=('GET', 'POST'))
def edit_config():
    access_key_id = get_form_param('AccessKeyId', type='string')
    access_key_secret = get_form_param('AccessKeySecret', type='string')
    region = get_form_param('Region', type='string')
    oss_access_endpoint = get_form_param('OssAccessEndpoint', type='string')
    oss_access_bucket = get_form_param('OssAccessBucket', type='string')
    oss_access_prefix = get_form_param('OssAccessPrefix', type='string')
    change = True
    conf = Config.query.filter().first()
    if conf is None:
        conf = Config()
        conf.accessKeyId = access_key_id
        conf.accessKeySecret = access_key_secret
        conf.region = region
        conf.ossAccessEndpoint = oss_access_endpoint
        conf.ossAccessBucket = oss_access_bucket
        conf.ossAccessPrefix = oss_access_prefix
    else:
        if access_key_id is not None and access_key_id == conf.accessKeyId:
            change = False
        conf.accessKeyId = access_key_id or conf.accessKeyId
        conf.accessKeySecret = access_key_secret or conf.accessKeySecret
        conf.region = region or conf.region
        conf.ossAccessEndpoint = oss_access_endpoint or conf.ossAccessEndpoint
        conf.ossAccessBucket = oss_access_bucket or conf.ossAccessBucket
        conf.ossAccessPrefix = oss_access_prefix or conf.ossAccessPrefix
    db.session.add(conf)
    db.session.commit()
    if change or conf.project is None:
        project = 'img-face-server-%s' % conf.region
        status, response = _create_set(project)
        if status:
            conf.project = project
            conf.setId = response
            db.session.add(conf)
            db.session.commit()
        else:
            conf.project = None
            conf.setId = None
            db.session.add(conf)
            db.session.commit()
            raise CustomFlaskErr('CreateSetError')
    return jsonify({'Code': 'Success', 'Message': 'Success'})


@imm_config.route('getConfig', methods=('GET', 'POST'))
def get_config():
    config = Config.query.filter().first()
    if config is not None:
        config_data = config.to_dict()
    else:
        config_data = {
            'AccessKeyId': current_app.config['ACCESS_KEY_ID'],
            'AccessKeySecret': current_app.config['ACCESS_KEY_SECRET'],
            'Region': current_app.config['IMM_REGION'],
            'OssAccessEndpoint': current_app.config['OSS_TEST_ACCESS_ENDPOINT'],
            'OssAccessBucket': current_app.config['OSS_TEST_ACCESS_BUCKET'],
            'OssAccessPrefix': current_app.config['OSS_TEST_ACCESS_PREFIX'],
        }

    return jsonify({'Code': 'Success', 'Message': 'Success', 'Data': config_data})


def _create_set(project):
    try:
        config = Config.query.filter().first()
        access_key_id = config and config.accessKeyId or current_app.config['ACCESS_KEY_ID']
        access_key_secret = config and config.accessKeySecret or current_app.config['ACCESS_KEY_SECRET']
        imm_region = config and config.region or current_app.config['IMM_REGION']
        add_endpoint("imm", imm_region, "imm.%s.aliyuncs.com" % imm_region)
        my_client = Client(access_key_id, access_key_secret, imm_region, timeout=60)
        data = {'Project': project, 'Type': 'PhotoProfessional', 'CU': 10}
        status, response = sent_request(my_client, 'PutProjectRequest', data)
        if status == httplib.OK:
            set_status, set_response = sent_request(my_client, 'CreateFaceSetRequest', {'Project': project})
            if set_status == httplib.OK:
                return True, set_response['SetId']
        return False, 'CreateSetError'
    except:
        traceback.print_exc()
        raise CustomFlaskErr('UnknownError')


