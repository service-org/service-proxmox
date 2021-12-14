#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from service_client.core.client import BaseClientAPI

from .cluster import ClusterAPI


class JsonAPI(BaseClientAPI):
    """ Json接口类 """

    cluster = ClusterAPI()
