# -*-coding: utf-8-*-
from . import information
from flask import jsonify, current_app
from app.models import db, Information, InformationUpdate, Config
from app.util.get_request_param import get_form_param
from app.util.custom_error import CustomFlaskErr
from app.util.aliyun_api import sent_request, Client
import httplib
import time
import logging
import oss2
import traceback


# 编辑标注信息
@information.route('/editInfo', methods=('GET', 'POST'))
def edit_info():
    id = get_form_param('Id', type='int', not_none=True)
    gender = get_form_param('Gender', type='string')
    age = get_form_param('Age', type='int')
    yaw_angle = get_form_param('YawAngle', type='float')
    pitch_angle = get_form_param('PitchAngle', type='float')
    roll_angle = get_form_param('RollAngle', type='float')

    # LeftEyeStatus
    left_normal_glass_eye_open = get_form_param('LeftNormalGlassEyeOpen', type='float')
    left_no_glass_eye_close = get_form_param('LeftNoGlassEyeClose', type='float')
    left_occlusion = get_form_param('LeftOcclusion', type='float')
    left_no_glass_eye_open = get_form_param('LeftNoGlassEyeOpen', type='float')
    left_normal_glass_eye_close = get_form_param('LeftNormalGlassEyeClose', type='float')
    left_dark_glasses = get_form_param('LeftDarkGlasses', type='float')

    # RightEyeStatus
    right_normal_glass_eye_open = get_form_param('RightNormalGlassEyeOpen', type='float')
    right_no_glass_eye_close = get_form_param('RightNoGlassEyeClose', type='float')
    right_occlusion = get_form_param('RightOcclusion', type='float')
    right_no_glass_eye_open = get_form_param('RightNoGlassEyeOpen', type='float')
    right_normal_glass_eye_close = get_form_param('RightNormalGlassEyeClose', type='float')
    right_dark_glasses = get_form_param('RightDarkGlasses', type='float')

    # EyeGlassStatus
    left_eye_glass_status = get_form_param('LeftEyeGlassStatus', type='int')
    right_eye_glass_status = get_form_param('RightEyeGlassStatus', type='int')

    # Blur
    blur_threshold = get_form_param('BlurThreshold', type='float')
    blur_value = get_form_param('BlurValue', type='float')

    # FaceQuality
    face_quality_threshold = get_form_param('FaceQualityThreshold', type='float')
    face_quality_value = get_form_param('FaceQualityValue', type='float')

    # FaceRectangle
    rectangle_left = get_form_param('FaceRectangleLeft', type='int')
    rectangle_top = get_form_param('FaceRectangleTop', type='int')
    rectangle_width = get_form_param('FaceRectangleWidth', type='int')
    rectangle_height = get_form_param('FaceRectangleHeight', type='int')

    info = Information.query.filter_by(id=id).first()

    if info is not None:
        if info.addTime is None:
            raise CustomFlaskErr('UnknownError')
        info_update = InformationUpdate.query.filter_by(infoId=id).first()
        if info_update is None:
            info_update = InformationUpdate()
            info_update.infoId = id
            info_update.imgDirectory = info.imgDirectory
        func = lambda x, y: y if y != x else None
        info_update.gender = func(info.gender, gender)
        info_update.age = func(info.age, age)
        info_update.yawAngle = func(info.yawAngle, yaw_angle)
        info_update.pitchAngle = func(info.pitchAngle, pitch_angle)
        info_update.rollAngle = func(info.rollAngle, roll_angle)
        info_update.blurThreshold = func(info.blurThreshold, blur_threshold)
        info_update.blurValue = func(info.blurValue, blur_value)
        info_update.faceQualityThreshold = func(info.faceQualityThreshold, face_quality_threshold)
        info_update.faceQualityValue = func(info.faceQualityValue, face_quality_value)

        # LeftEyeStatus
        info_update.leftNormalGlassEyeOpen = func(info.leftNormalGlassEyeOpen, left_normal_glass_eye_open)
        info_update.leftNoGlassEyeClose = func(info.leftNoGlassEyeClose, left_no_glass_eye_close)
        info_update.leftOcclusion = func(info.leftOcclusion, left_occlusion)
        info_update.leftNoGlassEyeOpen = func(info.leftNoGlassEyeOpen, left_no_glass_eye_open)
        info_update.leftNormalGlassEyeClose = func(info.leftNormalGlassEyeClose, left_normal_glass_eye_close)
        info_update.leftDarkGlasses = func(info.leftDarkGlasses, left_dark_glasses)
        # RightEyeStatus
        info_update.rightNormalGlassEyeOpen = func(info.rightNormalGlassEyeOpen, right_normal_glass_eye_open)
        info_update.rightNoGlassEyeClose = func(info.rightNoGlassEyeClose, right_no_glass_eye_close)
        info_update.rightOcclusion = func(info.rightOcclusion, right_occlusion)
        info_update.rightNoGlassEyeOpen = func(info.rightNoGlassEyeOpen, right_no_glass_eye_open)
        info_update.rightNormalGlassEyeClose = func(info.rightNormalGlassEyeClose, right_normal_glass_eye_close)
        info_update.rightDarkGlasses = func(info.rightDarkGlasses, right_dark_glasses)

        # EyeGlassStatus
        info_update.leftEyeGlassStatus = func(info.leftEyeGlassStatus, left_eye_glass_status)
        info_update.rightEyeGlassStatus = func(info.rightEyeGlassStatus, right_eye_glass_status)

        # FaceRectangle
        info_update.faceRectangleTop = func(info.faceRectangleTop, rectangle_top)
        info_update.faceRectangleLeft = func(info.faceRectangleLeft, rectangle_left)
        info_update.faceRectangleWidth = func(info.faceRectangleWidth, rectangle_width)
        info_update.faceRectangleHeight = func(info.faceRectangleHeight, rectangle_height)

        info.updateTime = time.strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(info)
        db.session.add(info_update)
        db.session.commit()
        return jsonify({'Code': 'Success', 'Message': 'Success'})
    else:
        raise CustomFlaskErr('NotFound.%s' % 'Id')


# 获取face图片信息
@information.route('getInfo', methods=('GET', 'POST'))
def get_information():
    id = get_form_param('Id', type='int', not_none=True)
    info_query = db.session.query(Information)
    info = info_query.filter_by(id=id).first()
    if info is not None:
        face_id = info.faceId
        next_filter = (Information.imgDirectory == info.imgDirectory, Information.id > info.id)
        next_res = info_query.with_entities(Information.id).filter(*next_filter).order_by(Information.id).first()
        next_id = next_res and next_res[0] or None
        img_url = _get_img_url(info)
        record = _get_info_updated_record(info)
        if info.addTime is not None:
            if info.updateTime is not None:
                info_update = InformationUpdate.query.filter_by(infoId=id).first()
            else:
                info_update = None
            if info_update is None:
                face_attribute = {
                    'Gender': {'Value': info.gender},
                    'Age': {'Value': info.age},
                    'HeadPose': info.to_head_pose(),
                    'EyeStatus': info.to_eye_status_dict(),
                    'Blur': {
                        'Blurness': {
                            'Threshold': info.blurThreshold,
                            'Value': info.blurValue
                        }
                    },
                    'FaceQuality': {
                        'Threshold': info.faceQualityThreshold,
                        'Value': info.faceQualityValue
                    }
                }
                info_data = {
                    'Id': id,
                    'FaceAttribute': face_attribute,
                    'FaceRectangle': info.to_face_rectangle_dict(),
                    'FaceId': face_id,
                    'EyeGlassStatus': info.to_eye_glass_status_dict()
                }
            else:
                face_attribute = {
                    'Gender': {'Value': info_update.gender or info.gender},
                    'Age': {'Value': info_update.age or info.age},
                    'HeadPose': _get_info_update_dict(info.to_head_pose(), info_update.to_head_pose()),
                    'EyeStatus': {
                                    'LeftEyeStatus': _get_info_update_dict(info.to_left_eye_status_dict(),
                                                                           info_update.to_left_eye_status_dict()),
                                    'RightEyeStatus': _get_info_update_dict(info.to_right_eye_status_dict(),
                                                                            info_update.to_right_eye_status_dict()),
                                },
                    'Blur': {
                        'Blurness': {
                            'Threshold': info_update.blurThreshold or info.blurThreshold,
                            'Value': info_update.blurValue or info.blurValue
                        }
                    },
                    'FaceQuality': {
                        'Threshold': info_update.faceQualityThreshold or info.faceQualityThreshold,
                        'Value': info_update.faceQualityValue or info.faceQualityValue
                    }
                }
                info_data = {
                    'Id': id,
                    'FaceAttribute': face_attribute,
                    'FaceRectangle': _get_info_update_dict(info.to_face_rectangle_dict(),
                                                           info_update.to_face_rectangle_dict()),
                    'FaceId': face_id,
                    'EyeGlassStatus': _get_info_update_dict(info.to_eye_glass_status_dict(),
                                                            info_update.to_eye_glass_status_dict())
                }
        # 尚未Index过的图片
        else:
            config = Config.query.filter().first()
            access_key_id = config and config.accessKeyId or current_app.config['ACCESS_KEY_ID']
            access_key_secret = config and config.accessKeySecret or current_app.config['ACCESS_KEY_SECRET']
            imm_region = config and config.region or current_app.config['IMM_REGION']
            oss_access_bucket = config and config.ossAccessBucket or current_app.config['OSS_TEST_ACCESS_BUCKET']
            my_client = Client(access_key_id, access_key_secret, imm_region, timeout=60)
            project = config and config.project or current_app.config['FACE_PROJECT']
            set_id = config and config.setId or current_app.config['FACE_SET_ID']
            data = {'Project': project,
                    'SrcUris': '["oss://%s/%s"]' % (oss_access_bucket, info.imgPath),
                    'SetId': set_id,
                    'Force': 1
                    }
            status, response = sent_request(my_client, 'IndexFaceRequest', data)
            if status == httplib.OK:
                if len(response['SuccessDetails']) == 0:
                    return jsonify({'Code': 'IndexActionProblem', 'Message': 'Please try again later.'})
                info_data = response['SuccessDetails'][0]['Faces'][0]
                face_attribute = info_data['FaceAttribute']
                gender = face_attribute['Gender']['Value']
                age = face_attribute['Age']['Value']
                head_pose = face_attribute['HeadPose']
                yaw_angle = head_pose['YawAngle']
                pitch_angle = head_pose['PitchAngle']
                roll_angle = head_pose['RollAngle']

                # LeftEyeStatus
                left_eye_status = face_attribute['EyeStatus']['LeftEyeStatus']
                left_normal_glass_eye_open = left_eye_status['NormalGlassEyeOpen']
                left_no_glass_eye_close = left_eye_status['NoGlassEyeClose']
                left_occlusion = left_eye_status['Occlusion']
                left_no_glass_eye_open = left_eye_status['NoGlassEyeOpen']
                left_normal_glass_eye_close = left_eye_status['NormalGlassEyeClose']
                left_dark_glasses = left_eye_status['DarkGlasses']

                # RightEyeStatus
                right_eye_status = face_attribute['EyeStatus']['RightEyeStatus']
                right_normal_glass_eye_open = right_eye_status['NormalGlassEyeOpen']
                right_no_glass_eye_close = right_eye_status['NoGlassEyeClose']
                right_occlusion = right_eye_status['Occlusion']
                right_no_glass_eye_open = right_eye_status['NoGlassEyeOpen']
                right_normal_glass_eye_close = right_eye_status['NormalGlassEyeClose']
                right_dark_glasses = right_eye_status['DarkGlasses']

                # Blur
                blur_threshold = face_attribute['Blur']['Blurness']['Threshold']
                blur_value = face_attribute['Blur']['Blurness']['Value']

                # FaceQuality
                face_quality_threshold = face_attribute['FaceQuality']['Threshold']
                face_quality_value = face_attribute['FaceQuality']['Value']

                # FaceRectangle
                face_rectangle = info_data['FaceRectangle']
                rectangle_left = face_rectangle['Left']
                rectangle_top = face_rectangle['Top']
                rectangle_width = face_rectangle['Width']
                rectangle_height = face_rectangle['Height']

                face_id = info_data['FaceId']

                info.gender = gender
                info.age = age
                info.yawAngle = yaw_angle
                info.pitchAngle = pitch_angle
                info.rollAngle = roll_angle
                info.blurThreshold = blur_threshold
                info.blurValue = blur_value
                info.faceQualityThreshold = face_quality_threshold
                info.faceQualityValue = face_quality_value

                # LeftEyeStatus
                info.leftNormalGlassEyeOpen = left_normal_glass_eye_open
                info.leftNoGlassEyeClose = left_no_glass_eye_close
                info.leftOcclusion = left_occlusion
                info.leftNoGlassEyeOpen = left_no_glass_eye_open
                info.leftNormalGlassEyeClose = left_normal_glass_eye_close
                info.leftDarkGlasses = left_dark_glasses
                # RightEyeStatus
                info.rightNormalGlassEyeOpen = right_normal_glass_eye_open
                info.rightNoGlassEyeClose = right_no_glass_eye_close
                info.rightOcclusion = right_occlusion
                info.rightNoGlassEyeOpen = right_no_glass_eye_open
                info.rightNormalGlassEyeClose = right_normal_glass_eye_close
                info.rightDarkGlasses = right_dark_glasses

                # EyeGlassStatus
                info.leftEyeGlassStatus = Information.get_eye_status(left_eye_status)
                info.rightEyeGlassStatus = Information.get_eye_status(right_eye_status)

                # FaceRectangle
                info.faceRectangleTop = rectangle_top
                info.faceRectangleLeft = rectangle_left
                info.faceRectangleWidth = rectangle_width
                info.faceRectangleHeight = rectangle_height

                info.faceId = face_id
                info.addTime = time.strftime('%Y-%m-%d %H:%M:%S')

                db.session.add(info)
                db.session.commit()
                info_data['Id'] = info.id
                info_data['EyeGlassStatus'] = info.to_eye_glass_status_dict()
            elif status == httplib.INTERNAL_SERVER_ERROR:
                return jsonify({'Code': 'IndexActionProblem', 'Message': 'Please try again later.', 'Next': next_id})
            else:
                logging.error('IndexActionError: %s' % str(response))
                raise CustomFlaskErr('UnknownError')

        return jsonify({'Code': 'Success', 'Message': 'Success',
                        'Data': {'Face': info_data, 'Next': next_id, 'ImgUrl': img_url, 'Record': record}})
    else:
        raise CustomFlaskErr('NotFound.%s' % 'Id')


# 获取图片url
def _get_img_url(info):
    config = Config.query.filter().first()
    access_key_id = config and config.accessKeyId or current_app.config['ACCESS_KEY_ID']
    access_key_secret = config and config.accessKeySecret or current_app.config['ACCESS_KEY_SECRET']
    oss_access_endpoint = config and config.ossAccessEndpoint or current_app.config['OSS_TEST_ACCESS_ENDPOINT']
    oss_access_bucket = config and config.ossAccessBucket or current_app.config['OSS_TEST_ACCESS_BUCKET']
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, oss_access_endpoint, oss_access_bucket)
    if info.imgExpires is not None and info.imgUrl is not None and info.imgExpires > int(time.time()):
        pass
    else:
        try:
            img_url = bucket.sign_url('GET', info.imgPath, 60*60*12)
            info.imgExpires = int(time.time()) + 60 * 60 * 12 - 600
            info.imgUrl = img_url
            db.session.add(info)
            db.session.commit()
        except:
            traceback.print_exc()
            raise CustomFlaskErr('UnknownError')
    return info.imgUrl


# 获取图片修改记录
def _get_info_updated_record(info):
    update_record = {}
    if info is not None:
        try:
            info_update = InformationUpdate.query.filter_by(infoId=info.id).first()
            column_list = ['Age', 'Gender', 'YawAngle', 'PitchAngle', 'RollAngle', 'LeftNormalGlassEyeOpen',
                           'LeftNoGlassEyeClose', 'LeftOcclusion', 'LeftNoGlassEyeOpen', 'LeftNormalGlassEyeClose',
                           'LeftDarkGlasses', 'RightNormalGlassEyeOpen', 'RightNoGlassEyeClose', 'RightOcclusion',
                           'RightNoGlassEyeOpen', 'RightNormalGlassEyeClose', 'RightDarkGlasses', 'BlurThreshold',
                           'BlurValue', 'FaceQualityThreshold', 'FaceQualityValue', 'FaceRectangleTop',
                           'FaceRectangleLeft', 'FaceRectangleHeight', 'FaceRectangleWidth', 'LeftEyeGlassStatus',
                           'RightEyeGlassStatus']
            if info_update is not None:
                for column in column_list:
                    # info_data = getattr(info, column[0].lower() + column[1:], None)
                    info_update_data = getattr(info_update, column[0].lower() + column[1:], None)
                    if info_update_data is not None:
                        update_record[column] = True
                    else:
                        update_record[column] = False
            else:
                for column in column_list:
                    update_record[column] = False
        except:
            traceback.print_exc()
            raise CustomFlaskErr('UnknownError')
        return update_record


def _get_info_update_dict(info_dict, info_update_dict):
    for key in info_dict:
        if info_update_dict.get(key, None) is not None:
            info_dict[key] = info_update_dict.get(key, None)
    return info_dict

