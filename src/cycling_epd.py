#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
JSONファイルからデータを読み込んでE-Paperに表示させる
"""
import sys
import os
import json
import time
import logging
from datetime import datetime

# dir
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13_V4
from PIL import Image,ImageDraw,ImageFont

DATA_FILE = '../log/cycling_data.json'
LOG_FILE = '../log/cycling_epd.log'

class CyclingEPDDisplay:
    def __init__(self):
        self.epd = None
        self.image = None
        self.draw = None
        self.fonts = {}
        self.last_data = {}

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                # logging.StreamHandler()
            ]
        )
        logging.info("電子ペーパー表示プログラム開始")

    def init_epd(self):
        """ Initialize e-Paper"""
        self.epd = epd2in13_V4.EPD()
        self.epd.init()
        self.epd.Clear(0xFF)

        # Setup FONT
        font_family = 'Font.ttf'
        font_family_bold = 'Font_bold.ttf'
        self.fonts = {
            'font12': ImageFont.truetype(os.path.join(picdir, font_family), 12),
            'font15': ImageFont.truetype(os.path.join(picdir, font_family), 15),
            'font15bold': ImageFont.truetype(os.path.join(picdir, font_family_bold), 15),
            'font40bold': ImageFont.truetype(os.path.join(picdir, font_family_bold), 40)
        }

        # Initialize Screen
        self.epd.init_fast()
        self.image = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.image)

        # Draw fixed elements
        self.draw_labels()
        self.epd.displayPartBaseImage(self.epd.getbuffer(self.image))

        logging.info("Complete Initialize E-Paper")
 

    def draw_labels(self):
        # frame
        self.draw.rectangle([(0,0),(250,122)], fill = 0xFF)
        self.draw.rectangle([(2,2),(246,120)], fill = 0x0)
        self.draw.rectangle([(4,4),(244,118)], fill = 0xFF)

        #data
        self.draw.text((6,6), '距離', font = self.fonts['font15'], fill = 0x0)
        self.draw.text((82,6), 'km', font = self.fonts['font15'], fill = 0x0)
        self.draw.text((6,101), 'スピード', font = self.fonts['font15'], fill = 0x0)
        self.draw.text((104,101), 'km/h', font = self.fonts['font15'], fill = 0x0)
        self.draw.text((150,101), '時間', font = self.fonts['font15'], fill = 0x0)
        self.draw.text((89,32), '消費カロリー', font = self.fonts['font15'], fill = 0x0)
        self.draw.text((213,72), 'kcal', font = self.fonts['font15'], fill = 0x0)
        self.draw.ellipse((15, 29, 77, 91), outline=0x0, fill = 0xFF)
        self.draw.ellipse((29, 43, 63, 77), outline=0x0, fill = 0xFF)

        # logo
        name = "UTAGE.GAMES" # あなたのチャンネル名に変更してください（任意）
        name_width = self.fonts['font15bold'].getlength(name)
        self.draw.rectangle([((246 - name_width - 6), 4),(246,23)], fill = 0x0)
        self.draw.text(((246 - name_width - 2), 4), name, font = self.fonts['font15bold'], fill = 0xFF)


    def load_data(self):
        """Load Json Data"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"データ読み込みエラー: {e}")

        return {
            'speed': 0.0,
            'distance': 0.0,
            'elapsed_time': '0:00:00',
            'calories': 0.0,
            'cadence': 0.0,
        }


    def update_display(self, data):
        """Update Display"""
        if not self.epd or not self.draw:
            return
        try:
            if data != self.last_data:
                # draw time
                self.draw.rectangle([(184, 101),(244, 116)], fill = 0xFF)
                self.draw.text((184, 101), data['elapsed_time'], font = self.fonts['font15bold'], fill = 0x0)

                # self.draw speed
                self.draw.rectangle([(70,101),(100, 116)], fill = 0xFF)
                self.draw.text((70, 101), f"{data['speed']:4.1f}", font = self.fonts['font15bold'], fill = 0x0)

                # self.draw distance
                self.draw.rectangle([(40, 6),(78, 21)], fill = 0xFF)
                self.draw.text((40, 6), f"{data['distance']:5.2f}", font = self.fonts['font15bold'], fill = 0x0)

                # self.draw cal
                self.draw.rectangle([(89, 47),(209, 87)], fill = 0xFF)
                self.draw.text((89, 47), f"{data['calories']:6.1f}", font = self.fonts['font40bold'], fill = 0x0)

                # self.draw cadence
                self.draw.ellipse((15, 29, 77, 91), outline=0x0, fill=0xFF)
                max_cadence = 120  # 想定する最大cadence値
                cadence_ratio = min(data['cadence'] / max_cadence, 1.0)  # 0-1の範囲に正規化
                end_angle = -90 + (360 * cadence_ratio)
                self.draw.pieslice([(15, 29), (77, 91)], start=-90, end=end_angle, fill=0x0)
                self.draw.ellipse((29, 43, 63, 77), outline=0x0, fill=0xFF)
                self.draw.text((31, 54), f"{data['cadence']:5.1f}", font = self.fonts['font12'], fill = 0x0)

                self.epd.displayPartial(self.epd.getbuffer(self.image))
                self.last_data = data.copy()

                logging.info(f"表示更新: {data['speed']}km/h, {data['distance']}km")

        except Exception as e:
            logging.error(f"Update Display Error: {e}")


    def check_data_freshness(self,data):
        """Check Data Freshness"""
        try:
            last_update = datetime.fromisoformat(data.get('last_update',''))
            time_diff = (datetime.now() - last_update).total_seconds()

            if time_diff > 10:
                logging.warning(f"データが古い可能性があります: {time_diff:1f}秒前")
                return False
            return True
        except:
            return False

    def run(self):
        """Main"""
        self.init_epd()

        if not self.epd:
            logging.error("E-Papger is not initialized")
            return 

        try:
            while True:
                data = self.load_data()
                self.check_data_freshness(data)
                self.update_display(data)
                time.sleep(1)

        except KeyboardInterrupt:
            logging.info("Display Program is halt...")

        except Exception as e:
            logging.error(f"Runtime Error: {e}")

        finally:
            if self.epd:
                logging.info("Change E-Papger to Sleep mode")
                self.epd.sleep()
                epd2in13_V4.epdconfig.module_exit(cleanup=True)


def main ():
    display = CyclingEPDDisplay()
    display.run() 

if __name__ == "__main__":
    main()
