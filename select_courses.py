#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:moddemod
# datetime:2019/8/30 22:28
# software: PyCharm

import requests as s
import json


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

    def get_course_select_turn_assoc(self):
        jump_url = 'http://jxglstu.hfut.edu.cn/eams5-student/for-std/course-select'
        self.requests.get(url=jump_url)
        post_url = 'http://jxglstu.hfut.edu.cn/eams5-student/ws/for-std/course-select/open-turns'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }
        data = 'bizTypeId=2&studentId={}'.format(self.get_info_id)
        res = self.requests.post(url=post_url, data=data, headers=headers)
        json_data = json.loads(res.text)
        for category in json_data:
            id = category['id']
            name = category['name']
            print(str(id) + '------' + name)

    def get_lesson_assoc(self, course_select_turn_assoc, lesson_code):
        url = 'http://jxglstu.hfut.edu.cn/eams5-student/ws/for-std/course-select/addable-lessons'
        data = 'turnId={}'.format(course_select_turn_assoc)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        lesson_assoc = []
        res = self.requests.post(url=url, data=data, headers=headers)
        json_data = json.loads(res.text)
        for lesson in json_data:
            for code in lesson_code:
                if code == lesson['code']:
                    lesson_assoc.append(lesson['id'])
                    print(lesson['id'], end='------')
                    print(lesson['course']['nameZh'], end='------')
                    print(lesson['code'], end='------')
                    print([teacher['nameZh'] for teacher in lesson['teachers'] if teacher['nameZh']])

        return lesson_assoc

    def select_course(self, lesson_assoc, course_select_turn_assoc, sec):
        url_add = self.baseUrl + "eams5-student/ws/for-std/course-select/add-request"
        url_add_r = self.baseUrl + "eams5-student/ws/for-std/course-select/add-drop-response"
        url_status = self.baseUrl + "eams5-student/ws/for-std/course-select/std-count"
        id = self.get_info_id
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }
        jump_url = self.baseUrl + 'eams5-student/for-std/course-select/{}/turn/{}/select'.format(self.get_info_id, course_select_turn_assoc)
        self.requests.get(url=jump_url)
        for lesson in lesson_assoc:
            while True:
                data = 'studentAssoc={}&lessonAssoc={}&courseSelectTurnAssoc={}&scheduleGroupAssoc=&virtualCost=0'.format(id, lesson, course_select_turn_assoc)
                requestId = self.requests.post(url=url_add, data=data, headers=headers).text
                data1 = 'studentId={}&requestId={}'.format(id, requestId)
                'studentId=100838&requestId=336f8798-252b-11ea-ac4d-005056830f9b'
                res = self.requests.post(url=url_add_r, data=data1, headers=headers)
                data_json = json.loads(res.text)
                if data_json['errorMessage']:
                    print(data_json['errorMessage'])
                data2 = 'lessonIds%5B%5D={}'.format(lesson)
                response = self.requests.post(url=url_status, data=data2, headers=headers)
                data_json = json.loads(response.text)
                print(data_json)
                # print('当前--' + str(lesson) + '--已选了' + str(data_json[lesson]) + '人...')
                import time
                time.sleep(sec)


def main():
    username = input("请输入学号：")
    password = input("请输入密码：")
    zhao = Login(username=username, password=password)
    print("欢迎" + zhao.get_real_username + "!")

    print('请输入你要选课的类型：(专业课，全校公选课，体育课)')
    zhao.get_course_select_turn_assoc()
    course_select_turn_assoc = input()

    t = input("请输入你的教学班代码：（如有多门课程请以空格分割输入例如：0115014B--001 0115014B--002）")
    lesson_code = t.split(" ")

    lesson_assoc = zhao.get_lesson_assoc(course_select_turn_assoc, lesson_code)

    sec = eval(input('请输入时间间隔:（0.5-~~）'))
    zhao.select_course(lesson_assoc, course_select_turn_assoc, sec)

    
if __name__ == '__main__':
    main()

