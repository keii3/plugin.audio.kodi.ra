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
    DATA_PATH = os.path.join(Const.DATA_PATH, 'misc')
    if not os.path.isdir(DATA_PATH): os.makedirs(DATA_PATH)
    # ファイル
    STATION_FILE = os.path.join(DATA_PATH, 'station.json')
    SETTINGS_FILE = os.path.join(DATA_PATH, 'settings.xml')


class Misc(Params, Jcba):

    def __init__(self, renew=False):
        # 放送局データをファイルから読み込む
        self.read()
        # 放送局データと設定データを初期化
        self.setup(renew)

    def read(self):
        self.data = read_json(Const.CHANNELS_FILE) or []

    def write(self):
        write_json(Const.CHANNELS_FILE, self.data)

    def setup(self, renew=False):
        # キャッシュがあれば何もしない
        if renew == False and os.path.isfile(self.STATION_FILE) and os.path.isfile(self.SETTINGS_FILE):
            return
        # 放送局データ
        buf = []
        for data in self.data:
            data['id'] = 'misc_%s' % md5(data['stream']).hexdigest()
            buf.append({
                'id': data['id'],
                'name': data['name'],
                'url': data.get('url',''),
                'logo_large': data.get('logo_large',''),
                'stream': data['stream']
            })
        # 放送局データを書き込む
        write_json(self.STATION_FILE, buf)
        # 設定データ
        buf = []
        for i, data in enumerate(self.data):
            buf.append(
                '    <setting label="{name}" type="bool" id="{id}" default="true" enable="eq({offset},2)" visible="true"/>'
                .format(id=data['id'], name=data['name'], offset=-1-i))
        # 設定データを書き込む
        write_file(self.SETTINGS_FILE, '\n'.join(buf))

    def getProgramData(self, renew=False):
        # jcba.pyから移設
        # 最新の番組データを取得、なければ放送局データから生成する
        results = [{'id': s['id'], 'progs': [{'title': s.get('onair') or Const.STR(30059)}]} for s in self.getStationData()]
        # デフォルトは更新なし
        nextupdate = '9' * 14
        return results, nextupdate

    def beginEdit(self, id):
        data = filter(lambda x:x['id']==id, self.getStationData())[0]
        Const.SET('id',id)
        Const.SET('name',data['name'])
        Const.SET('stream',data['stream'])
        Const.SET('logo',data.get('logo_large',''))
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)
        xbmc.executebuiltin('SetFocus(103)') # select 4th category
        xbmc.executebuiltin('SetFocus(201)') # select 2nd control

    def endEdit(self, id, name, stream, logo):
        if id == '':
            self.data.append({'name':name, 'stream':stream, 'logo':logo})
        else:
            target = filter(lambda x:x['id']==id, self.getStationData())[0]
            data = filter(lambda x:x['name']==target['name'] and x['stream']==target['stream'], self.data)[0]
            data['name'] = name
            data['stream'] = stream
            data['logo_large'] = logo
            # ロゴ画像があれば削除
            logopath = os.path.join(Const.MEDIA_PATH, 'logo_%s.png' % id)
            if os.path.isfile(logopath): os.remove(logopath)
        # 追加/編集した設定を書き込む
        self.write()
        # 変更を反映する
        self.setup(renew=True)
        # 設定ダイアログを更新する
        xbmc.executebuiltin('RunPlugin(%s?action=updateDialog)' % sys.argv[0])

    def delete(self, id):
        # 指定したidを除いた要素で配列を書き換える
        target = filter(lambda x:x['id']==id, self.getStationData())[0]
        self.data = filter(lambda x:x['name']!=target['name'] or x['stream']!=target['stream'], self.data)
        # 削除した設定を書き込む
        self.write()
        # 変更を反映する
        self.setup(renew=True)
        # 設定ダイアログを更新する
        xbmc.executebuiltin('RunPlugin(%s?action=updateDialog)' % sys.argv[0])
