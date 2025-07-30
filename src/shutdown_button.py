from gpiozero import Button
from subprocess import call
import logging

LOG_FILE = '../log/shutdown.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        # logging.StreamHandler()  # 画面にも出力
    ]
)

# GPIO19をシャットダウンボタンに使用（GPIO20はサイクリング用）
shutdown_button = Button(19, pull_up=True, bounce_time=0.2)

def shutdown_system():
    logging.info("シャットダウンボタンが押されました")
    # 1秒間の長押しでシャットダウン
    call(['sudo', 'shutdown', '-h', 'now'])

# 1秒間の長押しでシャットダウン実行
shutdown_button.when_held = shutdown_system
shutdown_button.hold_time = 1


logging.info("シャットダウンボタン監視開始 (GPIO19, 1秒長押し)")

try:
    import signal
    signal.pause()  # 無限待機
except KeyboardInterrupt:
    pass