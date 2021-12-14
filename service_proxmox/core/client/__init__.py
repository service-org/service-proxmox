#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import time
import typing as t

from logging import getLogger
from service_green.core.green import cjson
from service_client.core.client import BaseClient
from service_proxmox.exception import ProxmoxError

from .apis.api2 import Api2API

logger = getLogger(__name__)


class ProxmoxClient(BaseClient):
    """ Proxmox通用连接类 """

    api2 = Api2API()

    def __init__(
            self,
            product: t.Text,
            login_user: t.Text,
            login_pass: t.Optional[t.Text] = None,
            pass_param: t.Optional[t.Dict[t.Text, t.Any]] = None,
            token_name: t.Optional[t.Text] = None,
            token_data: t.Optional[t.Text] = None,
            separators: t.Optional[t.Text] = None,
            verify_ssl: t.Optional[bool] = False,
            **kwargs: t.Any
    ) -> None:
        """ 初始化实例

        @param product: 产品名称
            pve: PVE
            pmg: PMG
            pbs: PBS
        @param login_user: 登录用户
        @param login_pass: 登录密码
        @param pass_param: 密码参数
        @param token_name: 令牌名称
        @param token_data: 令牌数据
        @param separators: 令牌分隔
            1. pve默认分割符=
            2. pmg默认分割符空
            3. pbs默认分割符:
        @param verify_ssl: 验证SSL?
        @param kwargs: 其它参数
        """
        self.product = product.upper()
        self.login_user = login_user
        self.login_pass = login_pass
        self.pass_param = pass_param or {}
        self.token_name = token_name
        self.token_data = token_data
        self.separators = separators or '='
        not verify_ssl and kwargs.setdefault('pool_options', {}).update(
            {'cert_reqs': 'CERT_NONE', 'assert_hostname': False}
        )
        # 密码验证模式令牌生成时间
        self._password_auth_birth_time = None
        # 密码验证模式令牌刷新周期
        self._password_auth_renew_age = 3600
        # 密码验证模式生成认证票据
        self._password_auth_auth_ticket = None
        # 密码验证模式生成的csrf
        self._password_auth_csrf_token = None
        super(ProxmoxClient, self).__init__(**kwargs)

    def get_apiauth(self) -> t.Text:
        """ 获取api认证

        @return: t.Text
        """
        return f'{self.product}APIToken={self.login_user}!{self.token_name}{self.separators}{self.token_data}'

    def get_pwdauth(self) -> t.Tuple[t.Text, t.Text]:
        """ 获取pwd认证

        @return: t.Tuple[t.Text, t.Text]
        """
        url = f'{self.base_url}/api2/json/access/ticket'
        data = cjson.dumps({'username': self.login_user, 'password': self.login_pass} | self.pass_param)
        rsp = super(ProxmoxClient, self).request(
            'POST', url, headers={'Content-Type': 'application/json'}, body=data
        )
        rsp_data = rsp.data.decode('utf-8')
        rsp_dict = cjson.loads(rsp_data)
        data = rsp_dict['data']
        if data is None: raise ProxmoxError(f"couldn't authenticate user {self.login_user}")
        self._password_auth_birth_time = time.time()
        return data['ticket'], data['CSRFPreventionToken']

    def set_pwdauth(self) -> None:
        """  设置pwd认证

        @return: None
        """
        logger.debug(f'start fetch ticket and csrf_token...')
        if self._password_auth_birth_time is None:
            self._password_auth_auth_ticket, self._password_auth_csrf_token = self.get_pwdauth()
            logger.debug(f'got ticket={self._password_auth_auth_ticket} csrf_token={self._password_auth_csrf_token}')
        if time.time() - self._password_auth_birth_time >= self._password_auth_renew_age:
            self._password_auth_auth_ticket, self._password_auth_csrf_token = self.get_pwdauth()
            logger.debug(f'got ticket={self._password_auth_auth_ticket} csrf_token={self._password_auth_csrf_token}')

    def get_cookies(self) -> t.Text:
        """ 获取cookie

        @return: t.Text
        """
        cookie_name = f'{self.product}AuthCookie'
        cookie_data = self._password_auth_auth_ticket
        logger.debug(f'got cookies={cookie_name}={cookie_data}')
        return f'{cookie_name}={cookie_data}'

    def request(self, method: t.Text, url: t.Text, **kwargs: t.Any) -> t.Any:
        """ 请求处理方法

        :param method: 请求方法
        :param url: 请求地址
        :param kwargs: 请求参数
        :return: t.Any
        """
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 5.0
        if 'retries' not in kwargs:
            kwargs['retries'] = 2
        headers = kwargs.setdefault('headers', {})
        headers.update({
            'Content-Type': 'application/json'
        })
        self.token_name is not None and headers.update({
            'Authorization': self.get_apiauth()
        })
        self.login_pass is not None and self.set_pwdauth()
        self.login_pass is not None and headers.update({
            'Cookie': self.get_cookies(),
            'CSRFPreventionToken': self._password_auth_csrf_token
        })
        rsp = super(ProxmoxClient, self).request(method, url, **kwargs)
        return cjson.loads(rsp.data.decode('utf-8'))['data']
