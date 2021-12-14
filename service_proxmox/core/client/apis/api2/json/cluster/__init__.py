#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from service_client.core.client import BaseClientAPI

from .resources import ResourcesAPI


class ClusterAPI(BaseClientAPI):
    """ Cluster接口类 """

    resources = ResourcesAPI()
