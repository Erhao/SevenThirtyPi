# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO
import time


channel = 38


def driver(channel):
    data = [0 for i in range(40)]
    j = 0
    # 等待1s越过不稳定状态
    GPIO.setmode(GPIO.BOARD)
    time.sleep(1)
    # 发送开始(握手)信号
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.LOW)
    # 主线必须拉低18ms~30ms, 通知传感器准备数据(起始信号).这里选择20ms
    time.sleep(0.02)
    # 结束主线低电位, 保证低电位只持续18ms~30ms
    GPIO.output(channel, GPIO.HIGH)
    # 设置主线为输入口, 等待传感器的握手信号和数据信号
    GPIO.setup(channel, GPIO.IN)
    # 传感器把总线拉低83us, 再拉高87us, 以响应主机起始信号, 随后进入正式工作状态, 并开始发送数据
    while GPIO.input(channel) == GPIO.LOW:
        continue
    while GPIO.input(channel) == GPIO.HIGH:
        continue
    # 传感器收到主机起始信号后一次性发送40bit数据, 高位先出
    # 8bit湿度整数数据 + 8bit湿度小数数据 + 8bit温度证书数据 + 8bit温度小数数据 + 8bit校验和
    while j < 40:
        k = 0
        # 每一位信号都以54us低电平开始
        while GPIO.input(channel) == GPIO.LOW:
            continue
        # TODO: 为什么通过k的累加就可以知道高电平持续的时间?
        # 每一位的数值信号, 高电平的长短决定了数据位是0还是1
        # 数据"0"的格式为: 54us低电平 + 23us~27us高电平
        # 数据"1"的格式为: 54us低电平 + 68us~74us高电平
        while GPIO.input(channel) == GPIO.HIGH:
            k += 1
            if k > 100:
                break
        if k < 8:
            data[j] = 0
        else:
            data[j] = 1
        j += 1
    return data


# 数据转换为十进制
def compute(data):
    humidity_bit = data[0:8]# split data
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check_sum = 0
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7-i)
        humidity_point += humidity_point_bit[i] * 2 ** (7-i)
        temperature += temperature_bit[i] * 2 ** (7-i)
        temperature_point += temperature_point_bit[i] * 2 ** (7-i)
        check_sum += check_bit[i] * 2 ** (7-i)
    num = humidity + humidity_point + temperature + temperature_point
    return num, check_sum, temperature, humidity


def get_temp_humi():
    print('开始采集...')
    delay = 3

    res_list = []
    #采样20次
    while True:
        if len(res_list) > 20:
            break
        res = compute(driver(channel))
        res_list.append(res)
        time.sleep(delay)

    temperature_sum = 0
    humidity_sum = 0
    # 温度有效数据的个数
    temperature_num = 0
    # 湿度有效数据的个数
    humidity_num = 0
    for res in res_list:
        # 校验和一致则算作有效数据
        if res[0] == res[1]:
            temperature_sum += res[2]
            temperature_num += 1
            humidity_sum += res[3]
            humidity_num += 1
    if temperature_num == 0 or humidity_num == 0:
        print('本次数据采集循环内没有获取到有效数据！')
        return None, None

    # 取多个有效数据的平均值
    temperature_aver = temperature_sum / temperature_num
    humidity_aver = humidity_sum  / humidity_num
    print('有效数据:', temperature_aver, humidity_aver)
    return temperature_aver, humidity_aver
    
    # 第一次采集循环没有可供参考的上一次温度值, 故用不存在的值进行代替
    # if is_first:
    #     last_temperature_aver = 1000
    #     last_humidity_aver = 1000
    #     is_first = 0

    # 空气温度不可能在短时间内发生“剧变”
    # 保存上一次平均温度值与本次采集循环的最终值对比判断是否发生“剧变”
    # 当温度值发生"剧变"错误时, 往往采集到的湿度值也是不准确的, 故湿度值也沿用上一次的值
    # if last_temperature_aver != 1000:
        # 如果连续两次采集的温度数据之差大于3, 则认为发生了“剧变”
        # if abs(last_temperature_aver - temperature_aver) > 3:
            # print('本次数据有误，沿用上一次数据')
            # temperature_aver = last_temperature_aver
            # humidity_aver = last_humidity_aver
    # print('-----数据正常----- 温度: %.2f   湿度：%.2f%%    采集周期%ds' % (temperature_aver, humidity_aver, delay*10))
    # 保存本次采集循环的温度值和湿度值
    # last_temperature_aver = temperature_aver
    # last_humidity_aver = humidity_aver
