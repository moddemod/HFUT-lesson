#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： Administrator
# datetime： 2020/3/28 0028 下午 9:46 
# ide： PyCharm

import requests as req
import json
import tempfile
import base64
import time
import string
import random


class XueTangYun(object):
    xue_request = req.session()

    def __init__(self, username, password, captcha):
        self.base_url = 'https://hfut.xuetangx.com/'
        self.username = username
        self.password = password
        self.real_name = ''
        self.captcha = captcha
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }

        self.course_info = []
        self.course_info_detail_list = []
        self.done_list = []
        # self.login()

    def _before_login_check(self):
        import http.cookiejar as hc
        self.xue_request.cookies = hc.LWPCookieJar(filename='.c')
        try:
            self.xue_request.cookies.load(filename='.c')
        except FileNotFoundError:
            return False
        return True

    def _get(self, *args, **kwargs):
        return self.xue_request.get(headers=self.headers, *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self.xue_request.post(headers=self.headers, *args, **kwargs)

    def login(self):
        if not self._before_login_check():
            login_url = self.base_url + 'api/v1/oauth/number/login'
            captcha_key = self._get_captcha()
            self.captcha = input('please input captcha:')
            data = {
                'login': self.username,
                'password': self.password,
                'captcha': self.captcha,
                'captcha_key': captcha_key,
                'is_alliance': 0
            }
            self.headers['Content-Type'] = 'application/json; charset=utf-8'
            data = json.dumps(data)
            print(data)
            res = self._post(url=login_url, data=data)
            if res.status_code != 200:
                raise Exception('login error!')
            res_s = res.text
            print(res_s)
            j_info = json.loads(res_s)
            if j_info['message'] == 'ok':
                print('login success...')
                self.xue_request.cookies.save()
            self._set_real_name(j_info)

    def _set_real_name(self, d_str: dict):
        self.real_name = d_str['real_name']

    def get_real_name(self):
        return self.real_name

    def _get_captcha(self):
        c_url = self.base_url + 'api/v1/code/captcha'
        res = self._get(url=c_url)
        if res.status_code != 200:
            raise Exception('get captcha failed...')
        source_str = res.text
        # print(source_str)
        j_dic = json.loads(source_str)
        # print(j_dic)
        img_s = j_dic['data']['img']
        captcha_key = j_dic['data']['captcha_key']
        # print(img_s)
        print(captcha_key)
        img_b = base64.b64decode(img_s)
        filename = self._write_pic(img_b)
        self._show_pic(filename)
        return captcha_key

    def _write_pic(self, img_b):
        filename = tempfile.mkdtemp() + '.jpg'
        with open(filename, 'wb') as f:
            f.write(img_b)
        return filename

    def _show_pic(self, filename):
        from PIL import Image
        img = Image.open(filename)
        img.show()

    def set_course_info(self, page_size=10, page=1):
        url = self.base_url + 'mycourse_list?running_status=&term_id=' + self._get_term_id() + '&search=&page_size=' + \
              page_size.__str__() + '&page=' + page.__str__() + ''
        res = self._get(url=url)
        r_str = res.text
        d_str = json.loads(r_str)
        c_info_list = d_str['data']['results']
        for course_info in c_info_list:
            # print(course_info)
            print(course_info['course_id'])
            print(course_info['course_name'])
            print(course_info['class_id'])
            print(course_info['score'])
            print(course_info['recent_item'])
            try:
                print(course_info['recent_item']['data']['item_id'])
            except KeyError:
                print(0)
            print('+++++++++++++++++++++++++++++++++++++++++++')
            d_temp = dict()
            d_temp['course_id'] = course_info['course_id']
            d_temp['course_name'] = course_info['course_name']
            d_temp['class_id'] = course_info['class_id']
            d_temp['score'] = course_info['score']
            try:
                d_temp['item_id'] = course_info['recent_item']['data']['item_id']
            except KeyError:
                d_temp['item_id'] = 0
            self.course_info.append(d_temp)

    def _get_term_id(self):
        # url = self.base_url + 'api/v1/plat_term?plat_id=369'
        url = self.base_url + 'api/v1/plat_term?plat_id=' + self._get_plat_id()
        res = self._get(url=url)
        r_str = res.text
        print(r_str)
        d_str = json.loads(r_str)
        term_id = d_str['data'][-1]['term_id']  # 默认选择了最近的一个学期
        return str(term_id)

    def _get_plat_id(self):
        url = self.base_url + 'manager'
        res = self._get(url=url)
        cookies_jar = res.cookies
        cookies = req.utils.dict_from_cookiejar(cookies_jar)
        # print(cookies)
        # {'mode': '1', 'org_id': '503', 'plat_id': '369'}
        return cookies['plat_id']

    def handle_video(self, handle_num: int):
        """
        通过索引获取字典信息
        :param handle_num: 课程的信息列表索引
        :return:
        """
        class_id = self.course_info[handle_num]['class_id']
        course_id = self.course_info[handle_num]['course_id']
        url = self.base_url + 'score/' + str(course_id) + '/?class_id=' + class_id + '&if_cache=1'
        pass

    def _set_course_detail_info(self, handle_num: int):
        class_id = self.course_info[handle_num]['class_id']
        course_id = self.course_info[handle_num]['course_id']
        url = self.base_url + 'lms/api/v1/course/' + str(course_id) + '/courseware/'
        data = {
            'class_id': class_id
        }
        data = json.dumps(data)
        self.headers['Content-Type'] = 'application/json; charset=utf-8'
        res = self._post(url=url, data=data)
        r_str = res.text
        d_str = json.loads(r_str)
        print(d_str['data'])
        d_list = d_str['data']
        # print('+++++++++++++++++++++++++++++++++++++')
        # for info in d_list[:-1]:
        #     print(info)
        #     print(info['unit_name'])
        #     children = []
        #     try:
        #         children = info['children']
        #     except KeyError:
        #         print(None)
        #         continue
        #     for child in children:
        #         print(child['unit_name'])
        #         try:
        #             print(child['items'][0]['item_id'])
        #         except KeyError:
        #             print(0)
        # print('++++++++++++++++++++++++++++++++++++++')

        for info in d_list:
            temp_dict = dict()
            print(info)
            print(info['unit_name'])
            temp_dict['unit_name'] = info['unit_name']
            children = []
            try:
                children = info['children']
                videosRecord = info['videosRecord']
            except KeyError:
                continue
            children_list = []
            done = videosRecord['done']
            self.done_list += done
            for child in children:
                t_dict = dict()
                # print(child['unit_name'])
                t_dict['unit_name'] = child['unit_name']
                try:
                    # print(child['items'][0]['item_id'])
                    t_dict['item_id'] = child['items'][0]['item_id']
                except KeyError:
                    t_dict['item_id'] = '0'
                children_list.append(t_dict)
                print(t_dict)

            print(children_list)
            temp_dict['children'] = children_list
            self.course_info_detail_list.append(temp_dict)
        print(self.course_info_detail_list)

    def _get_et_and_sp(self, index):
        et = ''
        sp = '2'
        if index == 1:
            et = 'loadstart'
            sp = '1'
        elif index == 2:
            et = 'loadeddata'
            sp = '1'
        elif index == 3:
            et = 'play'
            sp = '1'
        elif index == 4:
            et = 'playing'
            sp = '1'
        elif index == 5:
            et = 'ratechange'
        else:
            et = 'heartbeat'
        return et, sp

    def view_video(self, handle_num: int, item_id):
        class_id = self.course_info[handle_num]['class_id']
        course_id = self.course_info[handle_num]['course_id']
        duration, user_id = self.get_duration_and_user_id(item_id=item_id, class_id=class_id)
        _st = self.get_timestamp_and_random()

        _pg = self.get_random_str(5)
        count = 0
        cp = 0
        while True:
            count += 1
            cp = (count - 1) * 10
            et, sp = self._get_et_and_sp(count)
            if int(cp) > int(duration):
                break
            if count == 1:
                query_str_parameters = 'i=5' \
                                       '&et=' + et + \
                                       '&p=web' \
                                       '&n=ws' \
                                       '&lob=cloud3' \
                                       '&cp=' + cp.__str__() + \
                                       '&fp=0' \
                                       '&tp=0' \
                                       '&sp=' + sp.__str__() + \
                                       '&ts=' + self.get_timestamp().__str__() + \
                                       '&u=' + user_id.__str__() + \
                                       '&c=' + course_id.__str__() + \
                                       '&v=' + item_id.__str__() + \
                                       '&cc=' + item_id.__str__() + \
                                       '&d=' + '0' + \
                                       '&pg=' + item_id.__str__() + '_' + _pg.__str__() + \
                                       '&sq=' + count.__str__() + \
                                       '&t=video' \
                                       '&_=' + _st.__str__()
            else:
                query_str_parameters = 'i=5' \
                          '&et=' + et + \
                          '&p=web' \
                          '&n=ws' \
                          '&lob=cloud3' \
                          '&cp=' + cp.__str__() + \
                          '&fp=0' \
                          '&tp=0' \
                          '&sp=' + sp.__str__() + \
                          '&ts=' + self.get_timestamp().__str__() + \
                          '&u=' + user_id.__str__() + \
                          '&c=' + course_id.__str__() + \
                          '&v=' + item_id.__str__() + \
                          '&cc=' + item_id.__str__() + \
                          '&d=' + duration.__str__() + \
                          '&pg=' + item_id.__str__() + '_' + _pg.__str__() + \
                          '&sq=' + count.__str__() + \
                          '&t=video' \
                          '&_=' + _st.__str__()
            _st += 1


            """
            et 播放动作 play pause 主要发送心跳包
            p
            n
            cp
            fp 0
            tp 0
            sp 播放倍速 0.5 1 1.5 2.0
            ts 时间戳
            u user_id
            c course_id
            v item_id
            cc
            d 视频时长
            pg 
            sq 播放视频从1开始依次+1
            _ 13位时间戳 与时间戳接近
            
            """
            fin_url = self.base_url + 'heartbeat?' + query_str_parameters
            ran_t = random.randrange(2, 4)
            # ran_t = ran_t // 10
            time.sleep(ran_t)
            print(fin_url)

            res = self._get(url=fin_url)
            r_str = res.text
            print(r_str)

        query_str_parameters = 'i=5' \
                               '&et=videoend' \
                               '&p=web' \
                               '&n=ws' \
                               '&lob=cloud3' \
                               '&cp=0'  \
                               '&fp=0' \
                               '&tp=0' \
                               '&sp=' + sp.__str__() + \
                               '&ts=' + self.get_timestamp().__str__() + \
                               '&u=' + user_id.__str__() + \
                               '&c=' + course_id.__str__() + \
                               '&v=' + item_id.__str__() + \
                               '&cc=' + item_id.__str__() + \
                               '&d=' + duration.__str__() + \
                               '&pg=' + item_id.__str__() + '_' + _pg.__str__() + \
                               '&sq=' + count.__str__() + \
                               '&t=video' \
                               '&_=' + _st.__str__()
        fin_url = self.base_url + 'heartbeat?' + query_str_parameters
        ran_t = random.randrange(2, 5)
        # ran_t = ran_t // 10
        time.sleep(ran_t)
        print(fin_url)

        res = self._get(url=fin_url)
        r_str = res.text
        print(r_str)
        print('该视频观看结束！...')

    def get_random_str(self, num):

        return ''.join(random.sample(string.ascii_letters + string.digits, num))

    def get_timestamp(self):
        """
        获取13位置时间戳
        :return:
        """
        return int(round(time.time() * 1000))

    def get_timestamp_and_random(self):
        fre = time.time().__str__()[0:8]
        suf = random.random().__str__()[2:7]
        result = fre + suf
        # print(result)
        return int(result)

    def get_duration_and_user_id(self, item_id, class_id):
        url = self.base_url + 'server/api/class_videos/?video_id=' + str(item_id) + '&class_id=' + str(class_id)
        res = self._get(url=url)
        r_str = res.text
        d_str = json.loads(r_str)
        print(d_str)
        duration = d_str['duration']
        user_id = d_str['user_id']
        return duration, user_id

    def start(self):
        import os
        self.login()
        self.set_course_info()
        print("你当前所选的课程有:")
        j = 0
        for c_info in self.course_info:
            j += 1
            print(str(j) + '、' + c_info['course_name'], "当前分数为: " + str(c_info['score']))

        index = input("请输入你要操作的课程序号：")
        handler = int(index) - 1
        self._set_course_detail_info(handler)
        item_id_list = []
        for course_info_detail in self.course_info_detail_list:
            print(course_info_detail['unit_name'])
            for info in course_info_detail['children']:

                print('+'*5, end='')
                if info['item_id'] != '0':
                    item_id_list.append(info['item_id'])
                # for i_d in self.done_list:
                #     if i_d == info['item_id']:
                #         print('\033[0;32;32m' + info['unit_name'] + '\033[0m')
                #         break
                if self.done_list.count(info['item_id']):
                    print('\033[0;32;32m' + info['unit_name'] + '\033[0m')
                else:
                    print(info['unit_name'])

        print('该课程总共有{}个视频！'.format(item_id_list.__len__()))
        print('当前已完成共计{}个！'.format(self.done_list.__len__()))
        rec = input('是否继续学习剩下视频？ yes/no')
        rec = rec.lower()
        if rec == 'yes' or rec == 'y':
            item_id_list = [item for item in item_id_list if item not in set(self.done_list)]
            for item_id in item_id_list:
                self.view_video(handler, item_id)
                # self._set_course_detail_info(handler)
                os.system("pause")
        elif rec == 'no' or rec == 'n':
            print('no')
        else:
            exit(0)

def test():
    username = ''
    password = ''
    captcha = ''
    xue = XueTangYun(username=username, password=password, captcha=captcha)
    xue.start()


if __name__ == '__main__':
    test()
