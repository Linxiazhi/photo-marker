# -*-coding: utf-8-*-
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(use_native_unicode='utf8')


class InformationBase(object):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.CHAR(6))
    age = db.Column(db.Integer)
    blurThreshold = db.Column(db.Float)
    blurValue = db.Column(db.Float)
    faceQualityThreshold = db.Column(db.Float)
    faceQualityValue = db.Column(db.Float)


    # RightEyeStatus
    rightNormalGlassEyeOpen = db.Column(db.Float)
    rightNoGlassEyeClose = db.Column(db.Float)
    rightOcclusion = db.Column(db.Float)
    rightNoGlassEyeOpen = db.Column(db.Float)
    rightNormalGlassEyeClose = db.Column(db.Float)
    rightDarkGlasses = db.Column(db.Float)

    # LeftEyeStatus
    leftNormalGlassEyeOpen = db.Column(db.Float)
    leftNoGlassEyeClose = db.Column(db.Float)
    leftOcclusion = db.Column(db.Float)
    leftNoGlassEyeOpen = db.Column(db.Float)
    leftNormalGlassEyeClose = db.Column(db.Float)
    leftDarkGlasses = db.Column(db.Float)

    # EyeGlassStatus 1: 佩戴眼镜 2: 佩戴墨镜 3: 未佩戴 4: 被遮挡 5: 不确定
    leftEyeGlassStatus = db.Column(db.SMALLINT)
    rightEyeGlassStatus = db.Column(db.SMALLINT)

    # FaceRectangle
    faceRectangleTop = db.Column(db.Integer)
    faceRectangleLeft = db.Column(db.Integer)
    faceRectangleWidth = db.Column(db.Integer)
    faceRectangleHeight = db.Column(db.Integer)

    # HeadPose
    yawAngle = db.Column(db.Float)
    pitchAngle = db.Column(db.Float)
    rollAngle = db.Column(db.Float)

    def to_dict(self):
        return {c.name[0].upper() + c.name[1:]: getattr(self, c.name, None) for c in self.__table__.columns}

    def to_face_rectangle_dict(self):
        face_rectangle_list = ['faceRectangleTop', 'faceRectangleLeft', 'faceRectangleWidth', 'faceRectangleHeight']
        return {c.name.replace('faceRectangle', ''):  getattr(self, c.name, None)
                for c in self.__table__.columns if c.name in face_rectangle_list}

    def to_head_pose(self):
        head_pose = ['yawAngle', 'pitchAngle', 'rollAngle']
        return {c.name[0].upper() + c.name[1:]: getattr(self, c.name, None)
                for c in self.__table__.columns if c.name in head_pose}

    def to_left_eye_status_dict(self):
        left_eye_status = ['leftNormalGlassEyeOpen', 'leftNoGlassEyeClose', 'leftOcclusion', 'leftNoGlassEyeOpen',
                           'leftNormalGlassEyeClose', 'leftDarkGlasses']
        return {c.name.replace('left', ''): getattr(self, c.name, None)
                for c in self.__table__.columns if c.name in left_eye_status}

    def to_right_eye_status_dict(self):
        right_eye_status = ['rightNormalGlassEyeOpen', 'rightNoGlassEyeClose', 'rightOcclusion', 'rightNoGlassEyeOpen',
                            'rightNormalGlassEyeClose', 'rightDarkGlasses']
        return {c.name.replace('right', ''): getattr(self, c.name, None)
                for c in self.__table__.columns if c.name in right_eye_status}

    def to_eye_status_dict(self):
        left_eye_status_dict = self.to_left_eye_status_dict()
        right_eye_status_dict = self.to_right_eye_status_dict()
        return {
            'LeftEyeStatus': left_eye_status_dict,
            'RightEyeStatus': right_eye_status_dict
        }

    def to_eye_glass_status_dict(self):
        return {
            'LeftEyeGlassStatus': self.leftEyeGlassStatus,
            'RightEyeGlassStatus': self.rightEyeGlassStatus
        }

    @staticmethod
    def get_eye_status(eye_status_dict, prefix=''):
        if eye_status_dict['%sNormalGlassEyeOpen' % prefix] + eye_status_dict['%sNormalGlassEyeClose' % prefix] > 50:
            status = 1
        elif eye_status_dict['%sDarkGlasses' % prefix] > 50:
            status = 2
        elif eye_status_dict['%sNoGlassEyeOpen' % prefix] + eye_status_dict['%sNoGlassEyeClose' % prefix] > 50:
            status = 3
        elif eye_status_dict['%sOcclusion' % prefix] > 50:
            status = 4
        else:
            status = 5
        return status


class Information(InformationBase, db.Model):
    __tablename__ = 'tb_info'
    imgDirectory = db.Column(db.String(100), index=True)
    imgPath = db.Column(db.String(100), unique=True, index=True)
    imgUrl = db.Column(db.String(320))
    imgExpires = db.Column(db.Integer)
    faceId = db.Column(db.String(32), index=True)

    addTime = db.Column(db.TIMESTAMP)
    updateTime = db.Column(db.TIMESTAMP)


class InformationUpdate(InformationBase, db.Model):
    __tablename__ = 'tb_info_update'
    infoId = db.Column(db.Integer, index=True)
    imgDirectory = db.Column(db.String(100), index=True)


class Config(db.Model):
    __tablename__ = 'tb_config'
    id = db.Column(db.Integer, primary_key=True)
    accessKeyId = db.Column(db.String(20))
    accessKeySecret = db.Column(db.String(32))
    region = db.Column(db.String(32))
    ossAccessEndpoint = db.Column(db.String(60))
    ossAccessBucket = db.Column(db.String(60))
    ossAccessPrefix = db.Column(db.String(60))
    project = db.Column(db.String(60))
    setId = db.Column(db.String(60))

    def to_dict(self):
        excludes = ('id', 'project', 'setId')
        return {c.name[0].upper() + c.name[1:]: getattr(self, c.name, None) for c in self.__table__.columns
                if c.name not in excludes}


