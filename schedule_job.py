# -*- encoding: utf-8 -*-

import os
import time
import shutil
import qiniu.config
import jwt
import requests
import json
import hashlib

from datetime import datetime, timedelta
from picamera import PiCamera
from stpi_config import stpi_config
from local_config import local_conf
from qiniu import Auth, put_file, etag


# 设置定时器
def print_time():
    """
        打印时间, 测试apscheduler
    """
    print("当前时间：", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])


def generate_img_path(now):
    """
        获取照片的存储路径
    """
    cur_path = now.strftime("%Y_%m_%d")
    abs_path = os.path.join(stpi_config.STATIC_DIR, cur_path)
    if not os.path.exists(abs_path):
        os.mkdir(abs_path)
    return abs_path


def get_time_pointer(hour, minute):
    """
        根据当前时间获取time_pointer, 范围为00~47
    """
    return '0' + str(hour * 2 + (0 if minute < 30 else 1)) if hour * 2 + (0 if minute < 30 else 1) < 10 else str(hour * 2 + (0 if minute < 30 else 1))


def generate_img_file_name(now):
    """
        获取图片文件名
    """
    time_pointer = get_time_pointer(now.hour, now.minute)

    # 获取随机摘要值切片
    md5 = hashlib.md5()
    md5.update((now.strftime("%Y%m%d_%H%M%S_") + time_pointer + '_stpenc').encode('utf-8'))
    hash_slice = md5.hexdigest()[:6]

    return 'STP_v01_' + \
        now.strftime("%Y%m%d_%H%M%S") + \
        '_' + \
        stpi_config.CAMERA_ID + \
        stpi_config.PLANT_ID + \
        '_' + \
        time_pointer + \
        '_' + \
        hash_slice


def take_photo():
    """
        定时拍照任务
    """
    now = datetime.now()
    path = generate_img_path(now)
    img_file_name = generate_img_file_name(now)

    full_file_name = path + '/' + img_file_name + '.jpg'
    camera = PiCamera()
    camera.start_preview()
    # 在拍照之前需要至少留给传感器2秒感光
    time.sleep(4)
    camera.capture(full_file_name)
    camera.stop_preview()
    camera.close()
    return now, img_file_name + '.jpg', full_file_name


def generate_stp_token(camera_id, dt):
    """
        生成请求STP SERVER的token
    """
    sign_data = {
        "camera_id": camera_id,
        "datetime": dt
    }
    token = jwt.encode(sign_data, local_conf.secret_salt, algorithm='HS256')
    return token


def upload_img_to_qiniu():
    now, file_name, full_file_name = take_photo()
    # 构建鉴权对象
    q = Auth(local_conf.qiniu['AccessKey'], local_conf.qiniu['SecretKey'])
    # 要上传的空间
    bucket_name = local_conf.qiniu['bucket_name']
    # 上传后保存的文件名
    key = file_name
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    # 要上传文件的本地路径
    localfile = full_file_name

    ret, info = put_file(token, key, localfile)
    if info.status_code != 200 or ret['key'] != key:
        return

    # 在STP数据库写入数据
    img_url = local_conf.qiniu['cdn_prefix'] + key
    stp_token = generate_stp_token(stpi_config.CAMERA_ID, now.strftime("%Y_%m_%d %H:%M:%S"))
    payload = {
        "token": str(stp_token, encoding='utf-8'),
        "img_url": img_url,
        "plant_id": int(stpi_config.PLANT_ID)
    }
    result = requests.post(local_conf.stp_server_save_img_url, data=json.dumps(payload)).json()
    # TODO(mbz): catch result
    return

def clean_img_trash():
    """
        每天0️点删除static目录下三天之前的目录
    """
    three_days_ago_path = os.path.join(stpi_config.STATIC_DIR, (datetime.now() + timedelta(days=-3)).strftime('%Y_%m_%d'))
    if os.path.exists(three_days_ago_path):
        shutil.rmtree(three_days_ago_path)
