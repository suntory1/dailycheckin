import os
import json
import time
import random
import hashlib
import requests
import urllib.parse

from dailycheckin import CheckIn

KEY = "3c5c8717f3daf09iop3423zafeqoi"
COOKIE_DATA = {"rq": "%2Fweb%2Fbook%2Fread"}
READ_URL = "https://weread.qq.com/web/book/read"
RENEW_URL = "https://weread.qq.com/web/login/renewal"


def encode_data(data):
    return '&'.join(f"{k}={urllib.parse.quote(str(data[k]), safe='')}" for k in sorted(data.keys()))


def cal_hash(input_string):
    _7032f5 = 0x15051505
    _cc1055 = _7032f5
    length = len(input_string)
    _19094e = length - 1

    while _19094e > 0:
        _7032f5 = 0x7fffffff & (_7032f5 ^ ord(input_string[_19094e]) << (length - _19094e) % 30)
        _cc1055 = 0x7fffffff & (_cc1055 ^ ord(input_string[_19094e - 1]) << _19094e % 30)
        _19094e -= 2

    return hex(_7032f5 + _cc1055)[2:].lower()


def get_wr_skey(headers, cookies):
    response = requests.post(RENEW_URL, headers=headers, cookies=cookies,
                             data=json.dumps(COOKIE_DATA, separators=(',', ':')))
    for cookie in response.headers.get('Set-Cookie', '').split(';'):
        if "wr_skey" in cookie:
            return cookie.split('=')[-1][:8]
    return None


class WXRead(CheckIn):
    name = "微信读书"

    def __init__(self, check_item):
        self.check_item = check_item

    def read(self, headers, cookies, data, total_read_time):
        print(f"微信读书开始阅读，本次阅读 {total_read_time} 秒")
        msg = []
        total_time = 0
        while total_time <= total_read_time:
            current_time = random.randint(20, 60)
            print(f"current read time is {current_time}")

            data['ct'] = int(time.time())
            data['ts'] = int(time.time() * 1000)
            data['rn'] = random.randint(0, 1000)
            data['sg'] = hashlib.sha256(f"{data['ts']}{data['rn']}{KEY}".encode()).hexdigest()
            data['s'] = cal_hash(encode_data(data))

            response = requests.post(READ_URL, headers=headers, cookies=cookies,
                                     data=json.dumps(data, separators=(',', ':')))
            resData = response.json()

            if 'succ' in resData:
                time.sleep(current_time)
                total_time = total_time + current_time
                print(f"✅ 阅读成功，阅读进度：{total_time} 秒")

            else:
                msg.append({"name": "认证信息", "value": "❌ cookie 已过期，尝试刷新..."})
                print(f"❌ cookie 已过期，尝试刷新...")
                new_skey = get_wr_skey(headers=headers, cookies=cookies)
                if new_skey:
                    cookies['wr_skey'] = new_skey
                    msg.append({"name": "认证信息", "value": f"✅ 密钥刷新成功，新密钥：{new_skey}"})
                    print(f"✅ 密钥刷新成功，新密钥：{new_skey}\n🔄 重新本次阅读")
                else:
                    print("❌ 无法获取新密钥，终止运行。")
                    msg.append({"name": "认证信息", "value": "❌ 无法获取新密钥，终止运行。"})
                    return msg
            data.pop('s')

        print(f"🎉 微信读书自动阅读完成！\n⏱️ 阅读时长：{total_time} 秒。")
        msg.append({"name": "微信读书", "value": f"🎉 微信读书自动阅读完成！\n⏱️ 阅读时长：{total_time} 秒。"})
        return msg

    def main(self):
        headers = self.check_item.get("headers")
        cookies = self.check_item.get("cookies")
        data = self.check_item.get("data")
        min_time = self.check_item.get("min")
        max_time = self.check_item.get("max")
        total_read_time = random.randint(min_time, max_time)
        msg = self.read(headers, cookies, data, total_read_time)
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    _check_item = datas.get("WXREAD", [])[0]
    print(WXRead(check_item=_check_item).main())
