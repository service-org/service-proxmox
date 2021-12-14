#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from service_client.core.client import BaseClientAPI

from .json import JsonAPI


class Api2API(BaseClientAPI):
    """ Api2接口类 """

    json = JsonAPI()
