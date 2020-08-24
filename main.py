import os
import flask
import json
import sys
from typing import Generic ,TypeVar
from flask import request,session,redirect,url_for
from flask import Flask




class AppController:
    defalutconfig={
        'port':5000,
        'session_timeout':7200,
        'authenmethod':'name',
        'secret_key':'secretkey',
    }

    defalutconfpath='/appconfig.json'

    @staticmethod
    def Get(config_name):
        controller=AppController()

        controller._config_name=config_name

        return controller

    def __init__(self):
        self._config_name=None
        self._config=None


    def _ReadConfig(self):
        if self._config_name is None:
            self._config_name = os.path.join(os.getcwd(), AppController.defalutconfpath)

        if not os.path.exists(self._config_name):
            with open(self._config_name,'w+') as outfile:
                json.dump(self.defalutconfig,outfile)


        with open(self._config_name) as config:
            self._config=json.load(config)

    def StartApp(self):
        self._ReadConfig()

        self.webprovider= WebProvider.Get()

        self.dataprovider=DataProvider.Get()

        self._authcator=AuthenProvider.GetAuthencator(self)

        self.webprovider.run(host="0.0.0.0",port=int(self._config['port']))



#provider by flask
class AuthenProvider:
    @staticmethod
    def GetAuthencator(controller):
        return FlaskAuthcator(controller)


class AuthcatorBase:
    def __init__(self,controller,param):
        pass


class FlaskAuthcator(AuthcatorBase):

    def __init__(self,controller,param=None):
        #TODO:input check
        app=controller.webprovider
        app.config['SECRET_KEY']=controller._config['secret_key']
        app.config['PERMANENT_SESSION_LIFETIME']=controller._config['session_timeout']

        @app.route('/')
        def VerifyUser():
            return '<p>输入账号 </p>'\
                '<form action="verify" method="post">\
                <input name="input_name"type="text" ></input>\
                <input type="submit">\
                </input>\
                </form>'\

        @app.route('/verify',methods=['Get','Post'])
        def ToVerify():
            uname=request.form['input_name']
            if uname == None:
                return 400
            elif uname not in controller.dataprovider.GetData('Users'):
                return '<p>非法用户，登录失败 </p>'

            session['username']=uname
            return redirect(url_for('FileBrowser'))


        @app.route('/filelist',methods=['Get','Post'])
        def FileBrowser():
            if session.get('username') is None:
                return  redirect(url_for('VerifyUser'))
            return 'test'

class WebProvider:
    _Instance=None

    @staticmethod
    def Get():
        if WebProvider._Instance is None:
            WebProvider._Instance=Flask(__name__)

        return WebProvider._Instance

class DataProvider:
    _Instance=None
    @staticmethod
    def Get():
        if DataProvider._Instance is None:
            DataProvider._Instance=DataProvider()

        return DataProvider._Instance

    def __init__(self):
        self._users = ['liuchanghe','wanglonglong']

        self._data = {'Users':lambda: self._GetUsers()}


    def GetData(self,key):
        return self._data['Users']()

    def _GetUsers(self):
        return self._users

if len(sys.argv) == 1:
    controller=AppController.Get(None)
    controller.StartApp()

