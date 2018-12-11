from flask import current_app
from aliyunsdkcore.client import AcsClient
from app.util.custom_error import CustomFlaskErr
import json
import logging
import os



class Client(AcsClient):
    def do_action_with_exception(self, acs_request):
        acs_request.set_accept_format('JSON')
        status, headers, body = self.implementation_of_do_action(acs_request)
        return status, json.loads(body)



def _create_request_by_namespace(api_namespace):
    try:
        pkg = __import__('aliyunsdkimm.request.v20170906.' + api_namespace, fromlist=True)
    except:
        os.system('pip install -U aliyunsdkimm')
        pkg = __import__('aliyunsdkimm.request.v20170906.' + api_namespace, fromlist=True)
    Request = getattr(pkg, api_namespace, None)
    return Request


def sent_request(my_client, request_namespace, data):
    Request = _create_request_by_namespace(request_namespace)
    request = Request()
    for key, value in data.items():
        if value is not None:
            request.add_query_param(key, value)
    try:
        status, response = my_client.do_action_with_exception(request)
        return status, response
    except Exception as e:
        logging.error(e)
        raise CustomFlaskErr('UnknownError')

