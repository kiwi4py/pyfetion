# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
import re

class PyFetion:

    # 保存cookie等会话信息
    _session = None

    # 发送者手机号&密码
    _mobile = None
    _password = None

    # 接收者飞信ID
    _uids = {}

    # 发送页面的csrf token
    _csrf_token = None;
    
    def __init__(self, mobile, password):
        self._mobile = mobile
        self._password = password 
        self._login()

    def __del__(self):
        self._logout()


    def _login(self):
        # first login
        uri = 'http://f.10086.cn/huc/user/space/login.do?m=submit&fr=space'
        data = { 'mobilenum':self._mobile, 'password':self._password, }
        self._post(uri, data=data)
        # then check, required!!! or you cann't send anything
        uri = 'http://f.10086.cn/im/login/cklogin.action'
        self._post(uri, data={})

    def send(self, mobile, message):
        '''发送消息'''
        if mobile == self._mobile:
            return self._to_myself(message)
        else:
            uid = self._get_uid(mobile)
            return self._to_uid(uid, message) if uid else ''

    def _logout(self):
        uri = 'http://f.10086.cn/im/index/logoutsubmit.action'
        result = self._post(uri)
        
        return result;

    def _to_myself(self, message):
        '''发送消息给自己'''
        uri = 'http://f.10086.cn/im/user/sendMsgToMyselfs.action'
        data = {'msg': message}
        result = self._post(uri, data=data)

        return result;

    def _to_uid(self, uid, message):
        '''发送消息给别人(uid)'''
        uri = 'http://f.10086.cn/im/chat/sendMsg.action?touserid=%s' % uid
        csrf_token = self._get_csrf_token(uid)
        data = { 'msg': message, 'csrfToken': csrf_token}
        result = self._post(uri, data=data)
        
        return result;

    def _post(self, url, data={}):
        if not self._session:
            self._session = requests.Session()

        resp = self._session.post(url, data=data)
        print url, data, resp.text
        return resp

    def  _get_uid(self, mobile):
        '''获取飞信ID'''
        if not self._uids.get(mobile):
            uri = 'http://f.10086.cn/im/index/searchOtherInfoList.action'
            data = {'searchText': mobile}
            result = self._post(uri, data=data)
            m =re.search(r'/toinputMsg\.action\?touserid=(\d+)', result.text)
            self._uids[mobile] = m.group(1) if m else ''
        
        return self._uids[mobile]

    def _get_csrf_token(self, uid):
        '''获取发送的csrf token'''
        if self._csrf_token is None:
            uri = 'http://f.10086.cn/im/chat/toinputMsg.action?touserid=%s' % uid
            result = self._post(uri)
            m = re.search(r'name="csrfToken".*?value="(.*?)"/', result.text)
            self._csrf_token = m.group(1) if m else ''

        return self._csrf_token


if __name__ == "__main__":
    username = '1381146XXXX'
    password = 'XXXXXX'
    f = PyFetion(username, password)
    f.send('1571120XXXX', '这是一条python发送的fetion测试短信')
