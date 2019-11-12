#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:moddemod
# datetime:2019/11/9 15:30
# software: PyCharm

import requests as s
import re
import os
import base64
from PIL import Image
from urllib import parse
import json
import time
import random


# Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0
class Chaoxing(object):
    def __init__(self, username, password, t=20):
        self.requests = s.Session()
        self.username = username
        self.password = password
        # self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0." \
        #                   "3809.87 Safari/537.36"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20200102 Firefox/70.0"
        self.cookie = ""
        self.t = t
        self.realName = ""
        self.name_lesson_list = []
        self.name_lesson_detail = []
        self.numberLesson = 0
        self.login()

    def login(self):
        login_url = "http://passport2.chaoxing.com/login"
        data_ = {
            "refer_0x001": "http%3A%2F%2Fi.mooc.chaoxing.com",
            "pid": -1,
            "pidName": "",
            "fid": 434,
            "fidName": '合肥工业大学',
            "allowJoin": 0,
            "isCheckNumCode": 1,
            "f": 0,
            'productid': '',
            't': 'true',
            'uname': self.username,
            'password': str(base64.b64encode(self.password.encode('utf-8')), 'utf-8'),
            'numcode': self.get_numcode(),
            'verCode': '',
        }
        data = parse.urlencode(data_)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.user_agent,

        }
        response = self.requests.post(url=login_url, data=data, headers=headers)
        # print(response.text)
        cookie_dict = response.cookies.get_dict()
        import json
        text = json.dumps(cookie_dict)
        # print(text)
        self.cookie = text.replace("{", "").replace("}", "").replace("\"", "").replace(": ", "=").replace(",", ";")
        # print(self.cookie)

    def get_numcode(self):
        """
        获取验证码后弹出来
        输入验证码：
        :return:
        """
        numcode_gen_url = "http://passport2.chaoxing.com/num/code?1573286587312"
        res = self.requests.get(url=numcode_gen_url, headers={"User-Agent": self.user_agent})
        numcode_name = "./numcode.png"
        with open(numcode_name, 'wb') as f:
            f.write(res.content)
        pic = Image.open(numcode_name)
        pic.show()
        numcode = input("请输入验证码：")
        os.remove(numcode_name)
        return numcode

    def get_vercode(self):
        pass

    def get_my_learn_lesson(self):
        ajax_url = "http://mooc1-1.chaoxing.com/visit/courses/study?isAjax=true&fileId=0&debug=false"
        html = self.requests.get(url=ajax_url, headers={'User-Agent': self.user_agent}).text
        # print(html)
        pattern = re.compile(r"'/mycourse/studentcourse\?courseId=(.*)&clazzid=(.*)&cpi=(.*)&enc=(.*)'")
        r_list = re.findall(pattern=pattern, string=html)  # 课程参数
        self.numberLesson = len(r_list)  # 课程数量
        # 课程的名字
        l_list = re.findall(r"target=\"_blank\" title=\"(.*)\">", html)
        for lesson_name in l_list:
            # print("%s: %s" % (l_list.index(lesson_name + 1), lesson_name))
            self.name_lesson_list.append(lesson_name)
        return r_list  # 返回课程参数

    def study(self, lesson, index):
        """
        :param index: 学习的序号，即是列表的序号index - 1
        :param lesson:一个列表 ['中国历史人文地理', '《梦溪笔谈》与传统文化的传承创新']
        :return:
        """
        href_list = self.query_lesson_detail(lesson=lesson[index])
        count = 0
        for href in href_list:
            # href = "https://mooc1-1.chaoxing.com" + href
            # 提取字段
            count += 1
            query = parse.urlparse(href).query
            params = parse.parse_qs(query)
            r_dict = {key: params[key][0] for key in params}
            json_mArg = json.loads("{}")
            for i in range(3):

                url = "http://mooc1-1.chaoxing.com/knowledge/cards?clazzid=" + r_dict['clazzid'] + "&courseid=" + \
                      r_dict[
                          'courseId'] + "&knowledgeid=" + r_dict['chapterId'] + "&num=" + str(i) + "&ut=s&cpi=" + \
                      lesson[index][2] + "&v=20160407-1"

                html = self.requests.get(url=url, headers={'User-Agent': self.user_agent}).text
                try:
                    r_ = re.findall(r'mArg = {(.*?)};', html)[0]
                    json_mArg = json.loads("{%s}" % r_)
                except Exception:
                    continue

                if len(json_mArg["attachments"]) > 0 and "name" in json_mArg["attachments"][0]["property"].keys():
                    if "isPassed" in json_mArg["attachments"][0].keys() and json_mArg["attachments"][0][
                        "isPassed"] == True:
                        print(self.name_lesson_detail[count - 1] + "已经学习过了...")
                        time.sleep(2)
                        break
                    else:
                        html1 = self.requests.get(
                            url="https://mooc1-1.chaoxing.com/ananas/status/%s?k=%s&flag=normal&_dc=%d" % (
                                json_mArg['attachments'][0]['property']['objectid'], json_mArg['defaults']['fid'],
                                int(round(time.time() * 1000))), headers={'User-Agent': self.user_agent}).text
                        # print(html1)
                        json_info = json.loads(html1)
                        # print(json_info)
                        print(r_dict)
                        # e = self.get_enc(r_dict['clazzid'], json_mArg['defaults']['userid'],
                        #                  json_mArg['attachments'][0]['jobid'],
                        #                  json_info['objectid'], json_info['duration'], json_info['duration'])
                        html2 = self.requests.get(
                            url="https://mooc1-1.chaoxing.com/multimedia/log/%s?objectId=%s&otherInfo=%s&clipTime=0_%s&rt=0.9&clazzId=%s&dtype=Video&duration=%s&jobid=%s&userid=%s&view=pc&playingTime=%s&isdrag=3&enc=%s" % (
                                json_info['dtoken'], json_info['objectid'], json_mArg['attachments'][0]['otherInfo'],
                                json_info['duration'], r_dict['clazzid'],
                                json_info['duration'], json_mArg['attachments'][0]['jobid'],
                                json_mArg['defaults']['userid'],
                                json_info['duration'],
                                self.get_enc(r_dict['clazzid'], json_mArg['defaults']['userid'],
                                             json_mArg['attachments'][0]['jobid'],
                                             json_info['objectid'], json_info['duration'], json_info['duration'])),
                            headers={'User-Agent': self.user_agent}).text
                        # html2 = self.requests.get(url=url, headers={'User-Agent': self.user_agent}).text
                        print(html2)
                        json_pass = json.loads(html2)
                        if (json_pass["isPassed"] == True):
                            print(self.name_lesson_detail[count - 1] + "学习完成！")
                        else:
                            print(self.name_lesson_detail[count - 1] + "学习失败！")
                            time.sleep(60)
                else:
                    continue

    def get_enc(self, clazzId, userid, jobid, objectId, duration, clipTime):
        import hashlib
        loc4 = duration
        text = "[%s][%s][%s][%s][%s][d_yHJ!$pdA~5][%s][0_%s]" % (
            clazzId, userid, jobid, objectId, str(loc4 * 1000), str(duration * 1000), clipTime)
        hash = hashlib.md5()
        hash.update(text.encode(encoding='utf-8'))
        return hash.hexdigest()

    def query_lesson_detail(self, lesson):
        """
        获取课程的具体目录信息
        :param lesson 课程的参数信息
        :return:
        """
        # 获取元组参数
        courseId = lesson[0]
        clazzid = lesson[1]
        cpi = lesson[2]
        enc = lesson[3]
        url = "https://mooc1-1.chaoxing.com/mycourse/studentcourse?courseId=" + courseId + "&clazzid=" + clazzid + \
              "&cpi=" + cpi + "&enc=" + enc
        html = self.requests.get(url=url, headers={'User-Agent': self.user_agent}).text

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.title.string)

        soup = soup.find('div', class_="content1 roundcorner")
        r = soup.findAll("a", {'data': '', 'id': '', 'style': '', 'target': ''})
        # num = 0
        self.name_lesson_detail = []
        for i in r:
            i = i.get('title')  # title获取标题，href获取学习地址
            if i == None:
                continue
            # num += 1
            # print("%s: %s" % (num, i))
            self.name_lesson_detail.append(i)
        href_list = []
        for href in r:
            href = href.get("href")
            if href == "javascript:void()":
                continue
            href_list.append(href)
        return href_list

    @property
    def real_name(self):
        """
        获取真实姓名
        :return:
        """
        url = "http://i.mooc.chaoxing.com/space/index?t=1573293287498"
        html = self.requests.get(url=url)
        self.realName = re.findall(r"<p class=\"personalName\" title=\"(.*)\" style=", html.text)[0]
        return self.realName

    @property
    def number_lesson(self):
        """
        获取课程的数量
        :return:
        """
        return self.numberLesson

    @property
    def name_lesson(self):
        """
        获取课程名字的列表
        :return:
        """
        return self.name_lesson_list

    @property
    def name_lesson_detail_(self):
        """
        获取每章节名字
        :return:
        """
        return self.name_lesson_detail


def main():
    username = input("请输入学号：")
    password = input("请输入密码：")
    # _time = int(input("请输入间隔时间："))
    zhao = Chaoxing(username=username, password=password)
    print("正在登录.......")
    time.sleep(3)
    print("欢迎" + zhao.real_name + "!")
    lesson = zhao.get_my_learn_lesson()  # 显示课程名字
    print("你当前有" + str(zhao.number_lesson) + "门选课")
    l_list = zhao.name_lesson
    for lesson_name in l_list:
        print("%s: %s" % (l_list.index(lesson_name), lesson_name))
    while True:
        try:
            index = int(input("请输入你要进行学习的课程的编号（例如0，1，2....）："))
            if index < 0 or index > zhao.number_lesson - 1:
                print("输入格式不对，请重新输入！")
                continue
            print("请输入你要进行的操作：")
            print("查询所有课程请输入:q")
            print("开始学习请输入:s")
            print("退出程序请输入:e")
            cmd = input("请输入你要进行的操作：")
            if cmd == "q":
                #  查询所有课程
                print("该课程目录如下：")
                print(zhao.query_lesson_detail(lesson[index]))
                d_list = zhao.name_lesson_detail_
                for name in d_list:
                    print("%s: %s" % (d_list.index(name) + 1, name))
            elif cmd == 's':
                #  开始学习
                zhao.study(lesson, index)
            elif cmd == 'e':
                exit(0)
            else:
                raise Exception
        except Exception:
            print("请按照规则正确输入！")

    # print("学习完成！")
    # os.system("pause")


if __name__ == '__main__':
    main()
