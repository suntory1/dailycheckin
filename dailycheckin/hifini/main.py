# -*- coding: utf-8 -*-
import json
import os
import traceback

import requests
from requests import utils

from bs4 import BeautifulSoup

from dailycheckin import CheckIn

class HiFiNi(CheckIn):
    name = "HiFiNi论坛"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def sign(session):
        url = "https://www.hifini.com/sg_sign.htm"
        try:
            r = session.post(url = url).json()
            print(f'response is {r.get("message")}')
            if r.get("message").find("成功") != -1 or r.get("message").find("已经签过") != -1:
                msg = [
                    {"name": "签到信息", "value": "签到成功或今日已经签到"},
                ]
            else:
                msg = [
                    {"name": "签到信息", "value": "签到失败，可能是cookie失效了！"},
                ]
        except Exception as e:
            msg = [
                {"name": "签到信息", "value": "无法正常连接到网站，请尝试改变网络环境，试下本地能不能跑脚本，或者换几个时间点执行脚本"},
                {"name": "错误信息", "value": str(e)}
            ]
        return msg

    def main(self):
        hifini_cookie = {item.split("=")[0]: item.split("=")[1] for item in self.check_item.get("cookie").split("; ")}
        session = requests.session()
        requests.utils.add_dict_to_cookiejar(session.cookies, hifini_cookie)
        session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                "x-requested-with": "XMLHttpRequest"
            }
        )
        msg = self.sign(session=session)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    _check_item = datas.get("HIFINI", [])[0]
    print(HiFiNi(check_item=_check_item).main())
