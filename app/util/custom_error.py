# -*-coding: utf8-*-
import logging

CODE_MSG = {
    'Missing': 'The parameter ${param} is missing.',
    'InvalidParameter': 'The parameter ${param} is not valid.',
    'UnknownError': 'The request has been failed due to some unknown error.',
    'NotFound': 'Specified ${param} is not found.',
    'OutOfRange': 'The input parameter ${param} doesn\'t match the limitation.',
}


class CustomFlaskErr(Exception):
    status_code = 400

    # 自己定义了一个 return_code，作为更细颗粒度的错误代码
    def __init__(self, return_code=None, status_code=None, payload=None):
        Exception.__init__(self)
        self.return_code = return_code
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    # 构造要返回的错误代码和错误信息的 dict
    def to_dict(self):
        rv = dict(self.payload or ())
        # 增加 dict key: return code
        if len(self.return_code.split('.')) > 1:
            code = self.return_code.split('.')[0]
            param = self.return_code.split('.')[1]
        else:
            code = self.return_code
            param = ''
        # 增加 dict key: message, 具体内容由常量定义文件中通过 return_code 转化而来
        rv['Message'] = CODE_MSG.get(code, None)
        rv['Code'] = self.return_code
        if rv['Message'] is None:
            logging.warning('Can not find the message by code.%s .' % code)
            rv['Message'] = 'UnknownError'
            rv['Code'] = 'UnknownError'
        rv['Message'] = rv['Message'].replace('${param}', param)

        return rv

