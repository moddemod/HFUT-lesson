import requests
import re
import threading
import time
import functools

req = requests.session()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'content-type': 'text/plain'
}

content_id = []
_id = []
pdf_url = []
threads = []


def request_mooc_get(url):
    return req.get(url=url)


def request_mooc_post(url, data):
    return req.post(headers=headers, cookies=cookies, url=url, data=data)


def get_timestamp():
    """
    获取13位置时间戳
    :return:
    """
    return int(round(time.time() * 1000))


def get_session_id(cookie: str):
    # NTESSTUDYSI=06f09fb95c634665aeeac99799a919fa;
    result = re.findall(r'NTESSTUDYSI=(\S+)[;]', cookie)
    if len(result) == 0:
        raise Exception('cookie error！')
    return result[0]


# url中tid=1206878228
def get_course_id():
    return str(_tid)


def set_course_id(tid):
    global _tid
    _tid = tid


def get_cookie():
    return cookies['cookie']


def set_cookie(cookie):
    global cookies
    cookies = dict(cookie=cookie)


def set_pdf_url():
    url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr'
    length = len(content_id)
    print(length)
    for i in range(length):
        try:
            print(content_id[i] + " " + _id[i])
        except IndexError:
            break
        data = {
            'callCount': 1,
            'scriptSessionId': '${scriptSessionId}190',
            'httpSessionId': get_session_id(cookies['cookie']),
            'c0-scriptName': 'CourseBean',
            'c0-methodName': 'getLessonUnitLearnVo',
            'c0-id': 0,
            'c0-param0': 'number:' + content_id[i],  # content_id
            'c0-param1': 'number:3',
            'c0-param2': 'number:0',
            'c0-param3': 'number:' + _id[i],  # section_id  1245454394
            'batchId': get_timestamp()
        }
        # print(data)
        res = req.post(url=url, cookies=cookies, data=data, headers=headers)
        con = res.text
        r = re.findall(r'textOrigUrl:"(.*)\.pdf"', con)
        # print(r)
        if len(r) == 0:
            continue
        pdf_url.append(r[0]+'.pdf')
        from urllib.parse import quote, unquote
        print('get ' + get_file_name(unquote(r[0])))
        # pdf_url.append(r[0])


# 1211971774 id
#
def get_course_info():
    url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLastLearnedMocTermDto.dwr'
    data = {
        "callCount": "1",
        "scriptSessionId": "${scriptSessionId}190",
        "httpSessionId": get_session_id(cookies['cookie']),
        "c0-scriptName": "CourseBean",
        "c0-methodName": "getLastLearnedMocTermDto",
        "c0-id": "0",
        "c0-param0": "number:" + get_course_id(),
        "batchId": get_timestamp()
    }
    r = request_mooc_post(url=url, data=data)
    # print(r)
    return r


def set_content_id(content: str):
    result = re.findall(r'contentId=(\d+);', content)
    print(result)
    print(len(result))
    global content_id
    content_id = result


def set_id(context: str):
    result = re.findall(r'id=(\d+);s.*jsonContent', context)
    print(result)
    global _id
    _id = result


def _time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print('Took ' + str(end - start))
    return wrapper


@_time
def start_download():
    for url in pdf_url:
        # r = get_file_name(visual_url)
        # print(r)
        t = threading.Thread(target=start_write, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("ok!")


def start_write(url):
    from urllib.parse import unquote
    result = request_mooc_get(url)
    visual_url = unquote(url)
    file_name = get_file_name(visual_url)
    print(file_name + ' downloading...')
    with open(file_name, 'wb') as f:
        # result.iter_content()
        # f.write(result.content)
        for chunk in result.iter_content(1024):
            f.write(chunk)


def get_file_name(url):
    result = re.findall(r'&download=(.*)', url)
    return result[0]


def main(tid, cookie):
    set_course_id(tid)
    set_cookie(cookie)
    c = get_course_info()
    context = c.text
    set_content_id(context)
    set_id(context)
    set_pdf_url()
    # print(pdf_url)
    print(len(pdf_url))
    start_download()


if __name__ == '__main__':
    """
    tid在url中直接复制即可
    cookie直接F12复制请求头里的cookie即可，复制完全，替换下面的cookie
    """
    tid = ''
    cookie = '' 
    main(tid, cookie)
