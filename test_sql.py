# -*- ecoding: utf-8 -*-
# @ModuleName: __init__.py
# @Function:
# @Author: liweijia
# @Time: 2024/3/20 10:20
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import  pymysql
tag = 1

db = pymysql.connect(
    host='localhost',
    user='root',
    password='liweijiaw',
    port=3306,
    db='dongchedi_vediodata'
)
cursor = db.cursor()
context = '''{'unique_id': 7349096079146942987, 'unique_id_str': '7349096079146942987', 'title': 'OMU越野装备！颜值担当#硬派越野 #牧马人 #牧马人改装', 'publish_time': 1711094770, 'watch_or_read_count': 0, 'has_video': True, 'image_list': None, 'user_info': {'avatar_url': 'https://p6-passport.byteacctimg.com/img/user-avatar/46806213beb7bdda6e5c0d140c60f1b4~300x300.image', 'name': '迈客改装', 'description': '这个人很懒，什么都没留下。', 'user_id': 101368842265, 'user_verified': False, 'verified_content': '', 'motor_auth_show_info': {'auth_v_type': 0, 'auth_v_desc': ''}}, 'video_info': {'cover_url': 'https://p3-dcd-sign.byteimg.com/tos-cn-p-0004/ca3aebcba3dd4b1fbadae502f0007221_1711094771~tplv-f042mdwyw7-original:640:0.image?rk3s=87dec8b9&x-expires=1711701329&x-signature=DRSXe88h6zKJstUcfePdrdjo7h4%3D', 'height': 720, 'width': 1280, 'video_id': 'v03004g10000cnujnsnog65mujjr0n00', 'video_type': 0, 'video_duration': 65, 'video_size': '{"ultra":{"duration":65.6,"file_size":8358265,"h":720,"w":1280}}'}, 'article_type': 2} OMU越野装备！颜值担当#硬派越野 #牧马人 #牧马人改装'''
title = 'dasfasdf'
sql = 'INSERT INTO vedio_data (detail_context,title) VALUES ("%s","%s");'

try:
    cursor.execute(sql,(context,title))
    db.commit()
    print('successful')
except:
    db.rollback()
    print('fail')
    tag = 0  # 失败设置0
db.close()
