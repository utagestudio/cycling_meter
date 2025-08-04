#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
回転数(num)を元に各種数値を計算してJSONファイルに保存する
"""
import json
import time
import logging
from datetime import datetime, timedelta
from collections import deque
import os
import random

from gpiozero import Button

# config
DATA_FILE = '../log/cycling_data.json'
LOG_FILE = '../log/cycling_calc.log'
RESET_FILE = './cycling_reset.flag'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        # logging.StreamHandler()
    ]
)

class CyclingDataCalculator:
    def __init__(self):
        self.wheel_circumference = 4.45
        self.calorie_factor = 0.065

        # GPIO SETTING
        self.cadence_pin = 20
        self.reset_pin = 5

        # Variables
        self.num = 0.0
        self.last_num = 0.0
        self.start_time = time.time()
        self.last_time = self.start_time

        # deque
        self.time_queue = deque([0.0] * 10, maxlen=10)
        self.num_queue = deque([0.0] * 10, maxlen=10)

        self.data = {
            'speed': 0.0,
            'distance': 0.0,
            'elapsed_time': '0:00:00',
            'calories': 0.0,
            'cadence': 0.0,
            'num': 0.0,
            'last_update': datetime.now().isoformat()
        }

        # INIT GPIO BUTTON
        self.setup_cadence_counter()
        self.setup_reset_button()

        logging.info("calculation start")
        logging.info(f"SWITCH PIN: GPIO{self.cadence_pin}")

    def setup_cadence_counter(self):
        """ Initialize a cadence button used gpiozero """
        try:
            self.button = Button(self.cadence_pin, pull_up=True)
            self.button.when_pressed = self.button_callback
            logging.info(f"Complete setup GPIO{self.cadence_pin} by gpiozero")

        except Exception as e:
            logging.error(f"Button Error: {e}")
            self.button = None

    def setup_reset_button(self):
        """ Initialize a reset button used gpiozero """
        try:
            self.reset_button = Button(self.reset_pin, pull_up=True, bounce_time=1)
            self.reset_button.when_pressed = self.reset_session
            logging.info(f"Complete setup GPIO{self.reset_pin} by gpiozero")

        except Exception as e:
            logging.error(f"Button Error: {e}")
            self.reset_button = None

    def button_callback(self):
        """ The function if a switch is pressed """
        try:
            self.num += 1.0
            logging.info(f"Pressed switch: {self.num}")

        except Exception as e:
            logging.error(f"Button Callback Error: {e}")

    def simulate_rotation(self):
        """ Simulation Cadence for Debug """
        self.num += random.uniform(1.8, 2.2)

    def calculate_values(self):
        """ calcuration """
        # 時間の差を検出
        current_time = time.time()

        if int(current_time) != int(self.last_time):
            #self.simulate_rotation() # for Debug

            # deque
            diff_time = current_time - self.last_time
            self.time_queue.append(diff_time)

            diff_num = self.num - self.last_num
            self.num_queue.append(diff_num)

            # 経過時間を作成
            elapsed_seconds = int(current_time - self.start_time)
            elapsed_time = str(timedelta(seconds=elapsed_seconds))
            if elapsed_seconds < 3600:
                elapsed_display = f"0{elapsed_time}"
            else:
                elapsed_display = elapsed_time

            # calculate num 毎分の回転数を計算
            if sum(self.time_queue) > 0:
                cadence = sum(self.num_queue) / sum(self.time_queue) * 60
            else:
                cadence = 0.0

            speed = cadence * self.wheel_circumference * 60 / 1000
            distance = self.num * self.wheel_circumference / 1000
            calories = self.num * self.calorie_factor

            self.data.update({
                'speed': round(speed, 1),
                'distance': round(distance, 2),
                'elapsed_time': elapsed_display,
                'calories': round(calories, 1),
                'cadence': round(cadence, 1),
                'num': round(self.num, 1),
                'last_update': datetime.now().isoformat()
            })

            self.save_to_json()

            logging.info(f"num: {self.num}, Speed: {speed:.1f}km/h, Distance: {distance:.2f}km, "
                    f"Calories: {calories:.1f}kcal, Cadence: {cadence:.1f}RPM")

            self.last_time = current_time
            self.last_num = self.num



    def save_to_json(self):
        """ save to json """
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Save to JSON Error: {e}")


    def check_reset_request(self):
        """ check reset request """
        try:
            if os.path.exists(RESET_FILE):
                file_time = os.path.getmtime(RESET_FILE)
                current_time = time.time()

                if current_time - file_time < 5:
                    self.reset_session()
                    os.remove(RESET_FILE)
                    logging.info("Execute reset request from web")
                else:
                    os.remove(RESET_FILE)

        except Exception as e:
            logging.error(f"Reset Request Check Error: {e}")

    def reset_session(self):
        """ Reset Session """

        self.num = 0.0
        self.last_num = 0.0
        self.start_time = time.time()
        self.last_time = self.start_time
        self.time_queue.clear()
        self.num_queue.clear()
        # キューを初期化
        for _ in range(10):
            self.time_queue.append(0)
            self.num_queue.append(0)

        logging.info("セッションがリセットされました")

    def cleanup_button(self):
        """ Clean Button """
        try:
            if hasattr(self, 'button') and self.button:
                self.button.close()
                logging.info("Complete clean button")
        except Exception as e:
            logging.error(f"Cleanup Button Error: {e}")


    def load_existing_data(self):
        """ load existing data for restart system"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    existing_data = json.load(f)
                    self.num = existing_data.get('num', 0.0)
                    self.last_num = self.num
                    logging.info(f"Existing Data Loaded: num={self.num}")

        except Exception as e:
            logging.error(f"Existing Data Load Error: {e}")

    def run(self):
        """Main"""
        self.load_existing_data()

        try:
            while True:
                self.check_reset_request()
                self.calculate_values()
                time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("System Halt...")
        except Exception as e:
            logging.error(f"Runtime Error: {e}")
        finally:
            logging.info("Finally...")
            self.cleanup_button()

def main():
    calculator = CyclingDataCalculator()
    calculator.run()

if __name__ == '__main__':
    main()

