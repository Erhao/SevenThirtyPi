# -*- encoding: utf-8 -*-

import os

from dataclasses import dataclass


@dataclass
class Config():
    """"
        配置类
    """

    # 基础配置
    STATIC_DIR = os.path.abspath(os.path.join(os.getcwd(), "static"))

    # 每个设备都不相同的配置
    CAMERA_ID = '01'
    PLANT_ID = '01'

    def __init__(self):
        if not os.path.exists(self.STATIC_DIR):
            os.mkdir(self.STATIC_DIR)


stpi_config = Config()
