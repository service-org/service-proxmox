#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from service_proxmox.core.client import ProxmoxClient
from service_proxmox.constants import PROXMOX_CONFIG_KEY
from service_core.core.service.dependency import Dependency


class Proxmox(Dependency):
    """ Proxmox依赖类 """

    name = 'Proxmox'

    def __init__(self, alias: t.Text, connect_options: t.Optional[t.Dict[t.Text, t.Any]] = None, **kwargs: t.Any):
        """ 初始化实例

        @param alias: 配置别名
        @param connect_options: 连接配置
        @param kwargs: 其它配置
        """
        self.alias = alias
        self.client = None
        self.connect_options = connect_options or {}
        super(Proxmox, self).__init__(**kwargs)

    def setup(self) -> None:
        """ 生命周期 - 载入阶段

        @return: None
        """
        connect_options = self.container.config.get(f'{PROXMOX_CONFIG_KEY}.{self.alias}.connect_options', default={})
        # 防止YAML中声明值为None
        self.connect_options = (connect_options or {}) | self.connect_options
        self.client = ProxmoxClient(**connect_options)

    def get_instance(self) -> ProxmoxClient:
        """ 获取注入对象

        @return: ProxmoxClient
        """
        return self.client
