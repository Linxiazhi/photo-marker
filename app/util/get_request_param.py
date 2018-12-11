# -*-coding: utf-8-*-
from flask import request, abort
from custom_error import CustomFlaskErr
import json
import logging


# 对请求参数进行类型判断和处理
def get_form_param(name, type='string', default=None, not_none=False):
    if name:
        param = request.form.get(name, default=default)
        if not_none is True:
            if param is None:
                raise CustomFlaskErr('Missing.%s' % name, status_code=400)
        if param is None and default is None:
            return param
        else:
            try:
                if type == 'string':
                    pass
                elif type == 'int':
                    param = int(param)
                elif type == 'float':
                    param = float(param)
                elif type == 'list' or type == 'dict':
                    param = json.loads(param)
                else:
                    logging.error('The param type.%s is not defined' % type)
                    raise CustomFlaskErr('UnknownError')
            except Exception as e:
                if isinstance(e, CustomFlaskErr):
                    raise e
                raise CustomFlaskErr('InvalidParameter.%s' % name)
        return param
    else:
        logging.error('Missing the param name.')
        abort(500)
