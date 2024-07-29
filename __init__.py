# -*- ecoding: utf-8 -*-
# @ModuleName: __init__.py
# @Function: 
# @Author: liweijia
# @Time: 2024/3/20 10:20
import random
import re
import threading
import requests  # 导入requests模块
import pymysql
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

from proxy_ip.tool import readaproxy


# 将数据插入数据库(封装为一个函数)
def insert(context, title):
    # 设置布尔标记，成功返回1，失败返回0
    tag = 1

    db = pymysql.connect(
        host='localhost',
        user='root',
        password='liweijiaw',
        port=3306,
        db='dongchedi_vediodata'
    )# 数据库信息

    cursor = db.cursor() # 启动数据库引擎
    sql = 'INSERT INTO vedio_data (detail_context,title) VALUES ("%s","%s");'

    try:
        cursor.execute(sql, (context, title)) # 执行sql语句
        db.commit()

    except pymysql.Error as e:
        print(e.args[0], e.args[1])
        db.rollback() # 回滚
        print('数据库fail')
        tag = 0  # 失败设置0

    db.close()
    return tag


def sanitize_filename(title):
    # 使用正则表达式来匹配并移除非法字符
    sanitized = re.sub(r'[\\/*?"<>|:#.？\x00-\x1f]', '', title)

    # 移除空格
    sanitized = sanitized.replace(' ', '')

    # 去除字符串两端的空白字符（包括空格、制表符、换行符等）
    sanitized = sanitized.strip()

    # 确保文件名不会过长
    max_length = 255  # 例如，Windows中某些文件系统的最大路径长度为260个字符，文件名长度会受此限制

    sanitized = sanitized[:max_length]

    return sanitized



def seleunim_(url, title):
    '''
    用于自动化获取视频链接并下载到本地video文件夹中
    :param url: 爬取网址
    :param title: 视频标题
    :return:
    '''
    # 创建Chrome浏览器选项对象
    opt = Options()
    # 使用无头模式
    opt.add_argument('--headless')

    # 禁止图片和css加载
    prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
    opt.add_experimental_option("prefs", prefs)

    opt.add_argument("--disable-gpu")  # 禁用gpu （加快速度）
    pa = webdriver.Chrome(options=opt)

    # 开始
    pa.get(url)
    pa.delete_all_cookies()  # 删除网页之前的cookie

    time.sleep(0.7)
    print(f'正在下载{title}')
    element = pa.find_element(By.XPATH,
                              "/html/body/div[1]/div/div/div/div/div[1]/div[1]/div/div[1]/div/div/div/video")  # 找到视频链接元素
    result = requests.get(element.get_attribute('src'))

    # 对标题进行处理 防止打开文件时出错
    title = sanitize_filename(title)
    # 保存视频链接到文件中
    with open(f"video/{title}.mp4", "wb") as f:
        f.write(result.content)
    print('-------' + title + '----下载成功')
    pa.quit()


if __name__ == '__main__':

    # 响应头池
    headers_stack = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    ]

    # 找到ajax发送的url，
    url = ('https://www.dongchedi.com/motor/pc/content/get_static?'
           'aid=1839&app_name=auto_web_pc&count=100&channel=news&page=1&article_type=video')

    # 随机获取一个User-Agent
    headers = {"User-Agent": headers_stack[random.randint(0, 4)]}

    # 随机从数据库中获取一个可用的代理ip
    proxy = {"http": readaproxy()[0]}

    # 解析返回的数据包 （数据包是json格式）
    response = requests.get(url, headers=headers, proxies=proxy, timeout=3)
    data = response.json()  # 解析json文件

    for i in range(1, 6):  # 1 to 6 exclude 6.
        # 内容(将字典转为string类型，以免发生不必要的错误)
        context = str(data['data']['news'][i])
        # 解析获取标题
        title = str(data['data']['news'][i]['title'])
        # 插入数据库
        if insert(context, title) == 0: print(f'{title}插入失败！')
        # 获取视频链接
        vedio_url = str(('https://www.dongchedi.com/video/'
                         + data['data']['news'][i]['unique_id_str']))

        time.sleep(0.5)  # 这里休眠的作用是因为如果循环太快，将会大于四个线程被启动（循环的速度大于while判断的速度）
        while threading.active_count() > 4:  # 限制一次性只能下载四个视频，当大于四个视频在下载时，会卡在循环里等待
            print(f'当前正有{threading.active_count() - 1}个视频在下载，等待中.......')  # -1代表不包括主进程
            time.sleep(8)

        # 获取视频（通过观察发现视频页面为为https://www.dongchedi.com/video+"unique_id_str"）由于网页是动态加载的，所以使用selenuim获取
        thread = threading.Thread(target=seleunim_, args=(vedio_url, title))  # 使用多线程技术，一次性爬取多个视频
        thread.start()
        print('线程启动')



