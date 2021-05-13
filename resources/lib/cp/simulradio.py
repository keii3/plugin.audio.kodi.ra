# -*- coding: utf-8 -*-

from jcba import Jcba

from resources.lib.const import *
from resources.lib.common import *

import os
import sys
import re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from hashlib import md5


class Params:
    # ファイルパス
    DATA_PATH = os.path.join(Const.DATA_PATH, 'simulradio')
    if not os.path.isdir(DATA_PATH): os.makedirs(DATA_PATH)
    # ファイル
    STATION_FILE = os.path.join(Const.TEMPLATE_PATH, 'cp', 'community', 'station_sr.json') # 放送局データ
    #SETTINGS_FILE = os.path.join(DATA_PATH, 'settings.xml')

    STN='simu_'

class Simulradio(Params, Jcba):

    def __init__(self, renew=False):
        return

    def setup(self, renew=False):
        # 放送局データを取得、設定ダイアログを書き出す
        return

    def getProgramData(self, renew=False):
        # jcba.pyから移設
        # 最新の番組データを取得、なければ放送局データから生成する
        results = [{'id': s['id'], 'progs': [{'title': s.get('onair') or Const.STR(30059)}]} for s in self.getStationData()]
        # デフォルトは更新なし
        nextupdate = '9' * 14
        return results, nextupdate
