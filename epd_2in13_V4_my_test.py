#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from datetime import datetime, timedelta
from collections import deque
import random

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in13_V4 My Demo")

    epd = epd2in13_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    font_family = 'Font.ttf'
    font15 = ImageFont.truetype(os.path.join(picdir, font_family), 15)
    font24 = ImageFont.truetype(os.path.join(picdir, font_family), 24)
    font40 = ImageFont.truetype(os.path.join(picdir, font_family), 40)

    time_queue = deque([0] * 10, maxlen=10)
    num_queue = deque([0] * 10, maxlen=10)


    logging.info("E-paper refresh")
    epd.init_fast()
    logging.info("Draw test")
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    draw.text((0,0), 'スピード: ', font = font15, fill = 0)
    draw.text((105,0), 'km/h', font = font15, fill = 0)
    draw.text((150,0), '距離: ', font = font15, fill = 0)
    draw.text((230,0), 'km', font = font15, fill = 0)
    draw.text((0,105), '時間: ', font = font15, fill = 0)
    draw.text((0,30), '消費カロリー', font = font15, fill = 0)
    draw.text((125,70), 'kcal', font = font15, fill = 0)
    epd.displayPartBaseImage(epd.getbuffer(image))

    num = 0
    last_num = num
    start_time = time.time()
    last_time = start_time

    while(True):
        # 時間の差を検出
        current_time = time.time()

        if int(current_time) != int(last_time):
            # deque
            diff_time = current_time - last_time
            time_queue.append(diff_time)
            num_queue.append(num - last_num)

            # 経過時間を作成
            elapsed_seconds = int(current_time - start_time)
            elapsed_time = str(timedelta(seconds=elapsed_seconds))
            if elapsed_seconds < 3600:
                elapsed_display = f"0{elapsed_time}"
            else:
                elapsed_display = elapsed_time

            # draw time
            draw.rectangle([(45,105),(105,120)], fill = 0xFF)
            draw.text((45,105), elapsed_display, font = font15, fill = 0)


            # draw speed
            # 毎分の回転数を計算
            cadence = sum(num_queue) / sum(time_queue) * 60
            draw.rectangle([(70,0),(105,15)], fill = 0xFF)
            draw.text((70,0), f"{cadence * 4.45 * 60 / 1000:4.1f}", font = font15, fill = 0)

            # draw distance
            distance = num * 4.45 / 1000
            draw.rectangle([(190,0),(230,15)], fill = 0xFF)
            draw.text((190,0), f"{distance:5.2f}", font = font15, fill = 0)

            # draw cal
            cal = num * 0.65
            draw.rectangle([(0,45),(120,95)], fill = 0xFF)
            draw.text((0,45), f"{cal:6.1f}", font = font40, fill = 0)
            epd.displayPartial(epd.getbuffer(image))

            last_time = current_time
            last_num = num
            num = num + random.uniform(1.8, 2.2)


    logging.info("Goto Sleep...")
    epd.sleep()


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()


