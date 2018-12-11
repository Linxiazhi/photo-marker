# -*-coding: utf-8-*-
from . import resource
from flask import current_app, jsonify
from app.models import db, Information, InformationUpdate, Config
from app.util.get_request_param import get_form_param
from app.util.custom_error import CustomFlaskErr
import oss2
import logging
import traceback


# 获取目录列表
@resource.route('/getDirectory', methods=('GET', 'POST'))
def get_directory():
    marker = get_form_param('Marker')
    config = Config.query.filter().first()
    access_key_id = config and config.accessKeyId or current_app.config['ACCESS_KEY_ID']
    access_key_secret = config and config.accessKeySecret or current_app.config['ACCESS_KEY_SECRET']
    oss_access_endpoint = config and config.ossAccessEndpoint or current_app.config['OSS_TEST_ACCESS_ENDPOINT']
    oss_access_bucket = config and config.ossAccessBucket or current_app.config['OSS_TEST_ACCESS_BUCKET']
    oss_access_prefix = config and config.ossAccessPrefix or current_app.config['OSS_TEST_ACCESS_PREFIX']
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, oss_access_endpoint, oss_access_bucket)
    directory_list = []
    try:
        times = 0
        while len(directory_list) < 5 and times < 10:
            oss_objects = bucket.list_objects(prefix=oss_access_prefix, marker=marker, max_keys=500)
            for obj in oss_objects.object_list:
                if obj.key.endswith('/'):
                    parent_directory = '/'.join(obj.key.split('/')[:-2]) + '/'
                    if parent_directory in directory_list:
                        directory_list.remove(parent_directory)
                    directory_list.append(obj.key)
            marker = oss_objects.next_marker
            times += 1
            if marker == '':
                break
        return jsonify({'Code': 'Success', 'Message': 'Success',
                        'Data': {'Directory': directory_list, 'NextMarker': marker}})
    except:
        traceback.print_exc()
        raise CustomFlaskErr('OssAccessError')


# 导入目录下图片资源
@resource.route('/importImgResource', methods=('GET', 'POST'))
def import_img_resource():
    directory = get_form_param('Directory', not_none=True)
    config = Config.query.filter().first()
    access_key_id = config and config.accessKeyId or current_app.config['ACCESS_KEY_ID']
    access_key_secret = config and config.accessKeySecret or current_app.config['ACCESS_KEY_SECRET']
    oss_access_endpoint = config and config.ossAccessEndpoint or current_app.config['OSS_TEST_ACCESS_ENDPOINT']
    oss_access_bucket = config and config.ossAccessBucket or current_app.config['OSS_TEST_ACCESS_BUCKET']
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, oss_access_endpoint, oss_access_bucket)
    # resource_list = []
    for obj in oss2.ObjectIterator(bucket, prefix=directory):
        # 通过is_prefix方法判断obj是否为文件夹。
        src_type = obj.key.split('.')[-1]
        if src_type in current_app.config['ALLOWED_EXTENSIONS']:
            if db.session.query(Information).filter_by(imgPath=obj.key).first() is None:
                new_info = Information()
                new_info.imgPath = obj.key
                new_info.imgDirectory = directory
                db.session.add(new_info)
    db.session.commit()
    return jsonify({'Code': 'Success', 'Message': 'Success'})


# 获取图片资源列表
@resource.route('/getImgResourceList', methods=('GET', 'POST'))
def get_img_resource_list():
    directory = get_form_param('Directory', not_none=True)
    key_word = get_form_param('KeyWord')
    page = get_form_param('Page', type="int", default=1)
    status = get_form_param('Status', type="int", default=0)
    limit = get_form_param('limit', type="int") or current_app.config["FLASKY_POSTS_PER_PAGE"]
    resource_list = []
    query_data = (Information.id, Information.imgPath, Information.addTime, Information.updateTime)
    query_filters = [Information.imgDirectory == directory]
    if key_word is not None and key_word != '':
        query_filters.append(Information.imgPath.like('%%%s%%' % key_word))
    status_filter = _deal_get_resource_status(status)
    if status_filter is not None:
        query_filters.append(status_filter)
    resource_info_query = Information.query.with_entities(*query_data).filter(*query_filters)
    try:
        resource_info_list = resource_info_query.paginate(page, limit)
    except:
        raise CustomFlaskErr('OutOfRange.Page')
    for resource in resource_info_list.items:
        add_time = resource[2] and resource[2].strftime('%Y-%m-%d %H:%M:%S') or resource[2]
        update_time = resource[3] and resource[3].strftime('%Y-%m-%d %H:%M:%S') or resource[3]
        resource_list.append({'Id': resource[0], 'Path': resource[1],
                              'AddTime': add_time, 'UpdateTime': update_time})
    return jsonify({'Code': 'Success', 'Message': 'Success', 'Data': {'Resources': resource_list},
                    'Total': resource_info_list.total})


# 清除目录下图片资源
@resource.route('/clearResource', methods=('GET', 'POST'))
def clear_resource():
    directory = get_form_param('Directory', not_none=True)
    try:
        Information.query.filter_by(imgDirectory=directory).delete()
        InformationUpdate.query.filter_by(imgDirectory=directory).delete()
    except Exception as e:
        logging.error('clearResource failed. %s' % e.message)
        raise CustomFlaskErr('UnknownError')
    return jsonify({'Code': 'Success', 'Message': 'Success'})


# 同步目录，删除不在当前根目录下所有文件
@resource.route('/synchronousResource', methods=('GET', 'POST'))
def synchronous_resource():
    try:
        config = Config.query.filter().first()
        access_key_id = config and config.accessKeyId or current_app.config['ACCESS_KEY_ID']
        access_key_secret = config and config.accessKeySecret or current_app.config['ACCESS_KEY_SECRET']
        oss_access_endpoint = config and config.ossAccessEndpoint or current_app.config['OSS_TEST_ACCESS_ENDPOINT']
        oss_access_bucket = config and config.ossAccessBucket or current_app.config['OSS_TEST_ACCESS_BUCKET']
        oss_access_prefix = config and config.ossAccessPrefix or current_app.config['OSS_TEST_ACCESS_PREFIX']
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, oss_access_endpoint, oss_access_bucket)
        directory_list = []
        try:
            for obj in oss2.ObjectIterator(bucket, prefix=oss_access_prefix):
                # 通过is_prefix方法判断obj是否为文件夹。
                if obj.key.endswith('/'):
                    parent_directory = '/'.join(obj.key.split('/')[:-2]) + '/'
                    if parent_directory in directory_list:
                        directory_list.remove(parent_directory)
                    directory_list.append(obj.key)
        except Exception as e:
            logging.error(e.message)
            raise CustomFlaskErr('OssAccessError')
        info_filter = []
        info_update_filter = []
        for directory in directory_list:
            info_filter.append(Information.imgDirectory != directory)
            info_update_filter.append(InformationUpdate.imgDirectory != directory)
        Information.query.filter(*info_filter).delete()
        InformationUpdate.query.filter(*info_update_filter).delete()
        return jsonify({'Code': 'Success', 'Message': 'Success'})
    except Exception as e:
        if isinstance(e, CustomFlaskErr):
            raise e
        logging.error('synchronous resource failed. %s' % e.message)
        raise CustomFlaskErr('UnknownError')


def _deal_get_resource_status(status):
    if status == 0:
        return None
    elif status == 1:
        return Information.updateTime.is_(None)
    elif status == 2:
        return Information.updateTime.isnot(None)
    else:
        raise CustomFlaskErr('InvalidParameter.Status')



