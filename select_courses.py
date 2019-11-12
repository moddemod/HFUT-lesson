#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:moddemod
# datetime:2019/8/30 22:28
# software: PyCharm

import requests as s


class Login(object):
    """登录"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.baseUrl = "http://jxglstu.hfut.edu.cn/"
        self.cookies = ""
        self.user_message_list = []
        self.requests = s.Session()
        self.login()

    def get_login_salt(self, suffix_url="eams5-student/login-salt"):
        """
        获取salt
        :param suffix_url:
        :return:
        """
        url = self.baseUrl + suffix_url
        text = self.requests.get(url).text
        return text

    def get_encrypt_password(self):
        """
        密码加密处理
        :return:
        """
        login_salt = self.get_login_salt() + "-" + self.password
        import hashlib
        hash1 = hashlib.sha1()
        hash1.update(login_salt.encode("utf-8"))
        return hash1.hexdigest()

    def login(self, suffix_url="eams5-student/login"):
        """
        登录逻辑
        :param suffix_url:
        :return:
        """
        url = self.baseUrl + suffix_url
        username = self.username
        password = self.get_encrypt_password()
        request_payload_dict = {
            "captcha": "",
            "password": password,
            "username": username
        }
        header = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }
        import json
        request_payload_json = json.dumps(request_payload_dict)
        response = self.requests.post(url=url, data=request_payload_json, headers=header, cookies=self.cookies)
        if response.status_code == 200 and json.loads(response.text)["result"] is True:
            self.get_real_message()
            print(self.requests.cookies.get_dict())
            return 1
        else:
            return 0

    # 下面的这些东西是因为之前打算写GUi写的，但是又没去写.......
    @property
    def get_info_id(self, suffix_url="eams5-student/for-std/student-info"):
        url = self.baseUrl + suffix_url
        response = self.requests.get(url=url)
        import re
        pattern = re.compile(r"\d+")
        number_id = re.findall(pattern, response.url).pop()
        return number_id

    @property
    def get_cookie(self):
        return self.cookies

    def get_real_message(self, suffix_url="eams5-student/for-std/student-info/info/"):
        url = self.baseUrl + suffix_url + self.get_info_id
        response = self.requests.get(url=url)
        import re
        pattern = re.compile(r"<span>(.*)</span>")
        self.user_message_list = re.findall(pattern, response.text)
        # print(type(self.user_message_list))

    @property
    def get_real_username(self):
        """
        姓名
        :return:
        """
        return self.user_message_list[1]

    @property
    def get_real_number_id(self):
        """
        身份证号
        :return:
        """
        return self.user_message_list[5]
    
    def get_courseSelectTurnAssoc(self):
        """
        获取courseSelectTurnAssoc
        这里我记得是某个url里的字段，可自行测试
        :return: 
        """
        return 666

    def select_course(self, lessonAssoc):
        url_add = self.baseUrl + "eams5-student/ws/for-std/course-select/add-request"
        url_add_r = self.baseUrl + "eams5-student/ws/for-std/course-select/add-drop-response"
        url_status = self.baseUrl + "eams5-student/ws/for-std/course-select/std-count"
        courseSelectTurnAssoc = self.get_courseSelectTurnAssoc()
        for lesson in lessonAssoc:
            while True:
                data = {
                    'studentAssoc': id,
                    'lessonAssoc': lesson,
                    'courseSelectTurnAssoc': courseSelectTurnAssoc,
                    'scheduleGroupAssoc': '',
                    'virtualCost': '0',
                }
                requestId = self.requests.post(url=url_add, data=data).text
                data1 = {
                    'studentId': id,
                    'requestId': requestId,
                }

                self.requests.post(url=url_add_r, data=data1)
                data2 = {
                    'lessonIds[]': lesson
                }

                response = self.requests.post(url=url_status, data=data2)
                print(response.text)
                import time
                time.sleep(1)
            # 写这个的时候是大一，因为现在没在选课时段，我也不好调试代码，所以这是一个死循环，你可以根据实际返回的值写个break条件
            # 零零碎碎的记忆，我是根据一个大四学长写的url写的，所以不百分百保证现在url有效，如果有问题可以联系我，qq 2456664655


def main():
    username = input("请输入学号：")
    password = input("请输入密码：")
    zhao = Login(username=username, password=password)
    print("欢迎" + zhao.get_real_username + "!")

    t = input("请输入你的lessonAssoc：（如有多门课程请以空格分割输入例如：777 888）")
    lessonAssoc = t.split(" ")
    zhao.select_course(lessonAssoc)
    zhao.select_course()
    
    
if __name__ == '__main__':
    main()

