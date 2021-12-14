#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from urllib.parse import urlencode
from service_client.core.client import BaseClientAPI


class ResourcesAPI(BaseClientAPI):
    """ Resources接口类 """

    def get(self, type: t.Text, **kwargs: t.Any) -> t.List[t.Dict[t.Text, t.Any]]:
        """ 获取集群资源

        doc: https://pve.proxmox.com/pve-docs/api-viewer/index.html#/cluster/resources

        @return: t.List[t.Dict[t.Text, t.Any]]
        """
        params = urlencode({'type': type})
        url = f'{self._base_url}/api2/json/cluster/resources?{params}'
        return self._get(url, **kwargs)
