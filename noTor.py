# -*- coding: gbk -*-
import time
import requests
import re
import _thread
import random
import os
from bs4 import BeautifulSoup
from ws4py.client.threadedclient import WebSocketClient
from faker import Faker


class CG_Client(WebSocketClient):

    def setIndex(self, index):
        self.index = index
        self.run = True

    def stop(self):
        self.run = False

    def changeID(self):
        self.send('42["request shortid",true]')

    def ping(self):
        time.sleep(pingInterval)
        if self.run == True:
            self.send("2")
            self.ping()
        else:
            return

    def opened(self):
        self.send("2probe")

    def received_message(self, resp):
        global shotID, count, signupCode
        response = str(resp)
        if response == "3probe":
            _thread.start_new_thread(self.ping, ())
            self.send("5")
            return
        if "shortid" in response:
            shotID[self.index] = re.search(r'"shortid","(.*?)"', response).groups()[0]
            return
        if "mail" in response:
            match = re.search(r"\d{6}<br>", response)
            if match:
                signupCode[self.index] = match.group(0).replace("<br>", "")
                # print("获取到的验证码:" + signupCode)
            return
        if response != "3":
            print(response)


def websocketRun(sid, index):
    global ws
    ws[index] = CG_Client('ws://' + apiDomain + '/socket.io/?EIO=3&transport=websocket&sid=' + sid)
    ws[index].setIndex(index)
    ws[index].connect()
    ws[index].run_forever()


def imFuckingCuming(index): #我他妈撸爆
    global shotID, signupCode, sid, count, error
    while True:
        # 获取websocket所需要的sid
        x = requests.get(
            httpConnect + apiDomain + "/socket.io/?EIO=3&transport=polling&t=" + str(int(time.time() * 1000)) + "-0")
        sid[index] = re.search(r'"sid":"(.*?)"', x.text).groups()[0]
        x = requests.get(httpConnect + apiDomain + "/socket.io/?EIO=3&transport=polling&t=" + str(
            int(time.time() * 1000)) + "-1&sid=" + sid[index])
        try:
            _thread.start_new_thread(websocketRun, (sid[index], index, ))
        except:
            print("无法启动线程")
        x = requests.post(httpConnect + apiDomain + "/socket.io/?EIO=3&transport=polling&t=" + str(
            int(time.time() * 1000)) + "-2&sid=" + sid[index], data='26:42["request shortid",true]')
        local = locals[random.randint(0, len(locals) - 1)]
        fake = Faker(local)
        header = {
            "X-Forwarded-For": fake.ipv4(network=True),
            "X-Real-IP": fake.ipv4(network=True),
            "User-Agent": fake.user_agent()
        }
        while shotID[index] is None:
            continue
        url = o365signupURL.replace("#email", shotID[index] + "%40" + apiDomain)
        sku = A1sku_Faculty if random.randint(1, 2) == 2 else A1sku_Student
        signupData = {
            "skug": "Education",
            "StepsData.Email": shotID[index] + "@" + apiDomain,
            "sku": sku
        }
        x = requests.post(url + sku, data=signupData, headers=header, verify=False)
        soup = BeautifulSoup(x.text, 'html.parser')
        WizardState = soup.find('input', id='WizardState')["value"]
        url = o365confirmAccount.replace("#email", shotID[index] + "%40" + apiDomain)
        lastName = fake.last_name()
        firstName = fake.first_name()
        password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
        # length -> 长度, special_chars -> 特殊字符, digits -> 数字, upper_case -> 大写字母, lower_case -> 小写字母, 这里定义随机密码规则
        while signupCode[index] is None:
            continue
        confirmAccountData = {
            "StepsData.FirstName": firstName,
            "StepsData.LastName": lastName,
            "StepsData.Password": password,
            "StepsData.RePassword": password,
            "StepsData.SignupCode": signupCode[index],
            "StepsData.EmailCheckboxChecked": "true",
            "StepsData.EmailCheckboxChecked": "false",
            "StepsData.PartnerAgreementCheckboxChecked": "false",
            "MessageId": "GenericError",
            "BackgroundImageUrl": "",
            "SkuId": sku,
            "Origin": "",
            "IsAdminSignup": "False",
            "CurrentWedcsTag": "/Signup/ConfirmAccount",
            "WizardState": WizardState,
            "WizardFullViewRendered": "True",
            "ShowCookiesDisclosureBanner": "False",
            "X-Requested-With": "XMLHttpRequest",
        }
        x = requests.post(url + sku, data=confirmAccountData, headers=header, verify=False)
        if "window.onbeforeunload=null;redirect=true;window.location = " in x.text:
            count += 1
            Account = "账号: " + shotID[index] + "@" + apiDomain + "\n" + "密码: " + password + "\n\n"
            with open(file[index], "a") as write:
                write.write(Account)
            print("第 " + str(count) + " 个账号, 使用的信息是: " + local)
        else:
            error += 1
            # print("第 " + str(error) + " 次错误, 请把信息提交给开发者: " + x.text)
            print("第 " + str(error) + " 次错误")
        signupCode[index] = None
        shotID[index] = None
        ws[index].stop()
        ws[index].close(code=1000, reason='')


requests.packages.urllib3.disable_warnings()
count = 0
error = 0
locals = ["zh_CN", "zh_TW", "en_US", "ja_JP"]
httpConnect = ""
apiDomain = ""
pingInterval = 25
pingTimeout = 60
threadCount = 10
# ↑这个是线程数量
ws = []
shotID = []
signupCode = []
file = []
sid = []
# count = 0
# error = 0
# shotID = None
# signupCode = None
# ws = None
o365signupURL = "https://signup.microsoft.com/signup?skug=Education&StepsData.Email=#email&sku="
o365confirmAccount = "https://signup.microsoft.com/signup/indexinternal?skug=Education&StepsData.Email=#email&sku="
A1sku_Faculty = "94763226-9b3c-4e75-a931-5c89701abe66"
A1sku_Student = "314c4481-f395-4525-be8b-2ec4bb1e9d91"

if __name__=="__main__":
    for i in range(threadCount):
        ws.append(None)
        shotID.append(None)
        signupCode.append(None)
        sid.append(None)
        file.append( apiDomain + '.' + str(i) + '.txt')
        _thread.start_new_thread(imFuckingCuming, (i, ))
    ls = None
    while ls != "STOP":
        ls = input("输入 STOP (全部大写) 才可以退出哦! 您处在:" + str(threadCount) + "线程模式中! 把他们撸爆吧!\r\n")

# print(x.text)
# fake = Faker("zh_TW")
# fake = Faker("en_US")
# fake = Faker("ja_JP")
# region 伪造信息所支持的国家，可以随意更换
# ar_EG - Arabic (Egypt)
# ar_PS - Arabic (Palestine)
# ar_SA - Arabic (Saudi Arabia)
# bg_BG - Bulgarian
# bs_BA - Bosnian
# cs_CZ - Czech
# de_DE - German
# dk_DK - Danish
# el_GR - Greek
# en_AU - English (Australia)
# en_CA - English (Canada)
# en_GB - English (Great Britain)
# en_IN - English (India)
# en_NZ - English (New Zealand)
# en_US - English (United States)
# es_ES - Spanish (Spain)
# es_MX - Spanish (Mexico)
# et_EE - Estonian
# fa_IR - Persian (Iran)
# fi_FI - Finnish
# fr_FR - French
# hi_IN - Hindi
# hr_HR - Croatian
# hu_HU - Hungarian
# hy_AM - Armenian
# it_IT - Italian
# ja_JP - Japanese
# ka_GE - Georgian (Georgia)
# ko_KR - Korean
# lt_LT - Lithuanian
# lv_LV - Latvian
# ne_NP - Nepali
# nl_NL - Dutch (Netherlands)
# no_NO - Norwegian
# pl_PL - Polish
# pt_BR - Portuguese (Brazil)
# pt_PT - Portuguese (Portugal)
# ro_RO - Romanian
# ru_RU - Russian
# sl_SI - Slovene
# sv_SE - Swedish
# tr_TR - Turkish
# uk_UA - Ukrainian
# zh_CN - Chinese (China)
# zh_TW - Chinese (Taiwan)
# endregion