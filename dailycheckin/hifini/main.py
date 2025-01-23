# -*- coding: utf-8 -*-
import json
import os
import re
import traceback

import requests
from requests import utils

from bs4 import BeautifulSoup

from dailycheckin import CheckIn

class HiFiNi(CheckIn):
    name = "HiFiNi论坛"

    def __init__(self, check_item):
        self.check_item = check_item

    def get_sign_value(self, cookies):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': cookies,
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': 'https://www.hifini.com/',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
        }

        response = requests.get(
            'https://www.hifini.com/sg_sign.htm', headers=headers)
        # print(response.text)

        pattern = r'var sign = "([\da-f]+)"'
        matches = re.findall(pattern, response.text)

        if matches:
            sign_value = matches[0]
            # print(f"sign value is {sign_value}")
            return sign_value
        else:
            if '登录后查看' in response.text:
                print("[-] Cookie失效")
                return None
            print("No sign value found.")
            return None

    def sign(self, cookie_str, session):
        msg = []
        sign_str = self.get_sign_value(cookie_str)

        if sign_str:
            url = "https://www.hifini.com/sg_sign.htm"
            try:
                data = {
                    'sign': sign_str
                }
                rsp = session.post(url = url, data = data)
                rsp_text = rsp.text.strip()
                # print(f'response is {rsp_text}')
                sign_result = ""
                if "已经签过" in rsp_text:
                    sign_result += '已经签到过了，不再重复签到!\n'
                    success = True
                elif "成功" in rsp_text:
                    rsp_json = json.loads(rsp_text)
                    sign_result += rsp_json['message']
                    success = True
                elif "503 Service Temporarily" in rsp_text or "502 Bad Gateway" in rsp_text:
                    sign_result += "服务器异常！\n"
                elif "请登录后再签到!" in rsp_text:
                    sign_result += "Cookie没有正确设置！\n"
                elif "操作存在风险，请稍后重试" in rsp_text:
                    sign_result += "没有设置sign导致的!\n"
                else:
                    sign_result += "未知异常!\n"
                    sign_result += rsp_text + '\n'

                if success:
                    msg.append({"name": "签到成功", "value": sign_result})
                else:
                    msg.append({"name": "签到失败", "value": sign_result})
            except Exception as e:
                msg.append({"name": "签到信息", "value": "无法正常连接到网站，请尝试改变网络环境，试下本地能不能跑脚本，或者换几个时间点执行脚本"})
                msg.append({"name": "错误信息", "value": str(e)})
        else:
            msg.append({"name": "hifini 签到异常", "value": "hifini 签到失败：没有获取到签名"})
        return msg

    def main(self):
        cookie_str = self.check_item.get("cookie")
        hifini_cookie = {item.split("=")[0]: item.split("=")[1] for item in self.check_item.get("cookie").split("; ")}
        session = requests.session()
        requests.utils.add_dict_to_cookiejar(session.cookies, hifini_cookie)
        session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': 'https://www.hifini.com/',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
        })
        msg = self.sign(cookie_str=cookie_str, session=session)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    _check_item = datas.get("HIFINI", [])[0]
    print(HiFiNi(check_item=_check_item).main())
