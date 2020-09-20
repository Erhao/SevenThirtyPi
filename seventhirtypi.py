# -*- encoding: utf-8 -*-

from multiprocessing import process
from typing import Optional
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from schedule_job import upload_img_to_qiniu, clean_img_trash
from mqtt_jobs import sub_watering_cmd, pub_soil_moisture
from local_config import local_conf
from multiprocessing import Process
from BH1750 import auto_light


app = FastAPI()


# 另起进程订阅MQTT消息(浇水)
sub_mqtt_watering_process = Process(target=sub_watering_cmd)
sub_mqtt_watering_process.start()

# 另起进程自动补光
auto_light_process = Process(target=auto_light)
auto_light_process.start()


@app.on_event('startup')
def init_scheduler():
    """
        初始化定时任务
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(upload_img_to_qiniu, 'cron', minute='0, 30')
    scheduler.add_job(clean_img_trash, 'cron', hour=0)
    # 检测土壤湿度并上报
    scheduler.add_job(pub_soil_moisture, 'cron', minute='0, 10, 20, 30, 40, 50')
    # scheduler.add_job(pub_soil_moisture, 'cron', second='0')

    scheduler.start()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
