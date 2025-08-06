from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import logging

DATA_FILE = '../log/cycling_data.json'
LOG_FILE = '../log/cycling_web.log'
RESET_FILE = './cycling_reset.flag'
PORT = 5000

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../templates',
            static_url_path='/static')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        # logging.StreamHandler()  # 画面にも出力
    ]
)

def load_cycling_data():
    logging.info("load data")
    try:
        if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    return data
    except Exception as e:
        logging.info(f"data load error: {e}")

    return {
        'speed': 0.0,
        'distance': 0.0,
        'elapsed_time': '0:00:00',
        'calories': 0.0,
        'cadence': 0.0,
        'num': 0.0,
        'last_update': datetime.now().isoformat()
    }

@app.route('/')
def index():
    """ main page """
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """ return data from API """
    data = load_cycling_data()

    try:
        last_update = datetime.fromisoformat(data.get('last_update',''))
        time_diff = (datetime.now() - last_update).total_seconds()
        data['data_age'] = time_diff
        data['is_fresh'] = time_diff < 10
    except:
        data['data_age'] = 999
        data['is_fresh'] = False

    return jsonify(data)

@app.route('/api/reset', methods=['POST'])
def reset_session():
    try:
        data = load_cycling_data()

        with open(RESET_FILE, 'w') as f:
            f.write(str(datetime.now().timestamp()))

        logging.info("Send request to reset")

        return jsonify({
            'status': 'success',
            'message': 'Sent request to session reset'
            })

    except Exception as e:
        logging.error(f"Reset Error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
            }), 500

@app.route('/api/status')
def get_status():
    data = load_cycling_data()

    try:
        last_update = datetime.fromisoformat(data.get('last_update', ''))
        time_diff = (datetime.now() - last_update).total_seconds()

        if time_diff < 5:
            status = 'online'
        elif time_diff < 30:
            status = 'slow'
        else:
            status = 'offline'
    except:
        status = 'unknown'

    return jsonify({
        'status': status,
        'last_update': data.get('last_update', ''),
        'data_file_exists': os.path.exists(DATA_FILE)
    })
 

@app.route('/api/log')
def get_log():
    """ログファイルの内容を返す（デバッグ用）"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                # 最新50行のみ返す
                return jsonify({
                    'log_lines': lines[-50:],
                    'total_lines': len(lines)
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'log_lines': [], 'total_lines': 0})

@app.errorhandler(404)
def page_not_found(e):
    """404エラーハンドラー"""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500エラーハンドラー"""
    return jsonify({'error': 'Internal server error'}), 500


def main():
    logging.info("エアロバイク Webサーバーを開始します...")
    logging.info(f"Data file: {DATA_FILE}")
    logging.info(f"PORT: {PORT}")
    logging.info(f"URL: http://localhost:{PORT}")
    logging.info(f"Network Access: http://raspberrypi.local:{PORT}")


    try:
        app.run(
            host='0.0.0.0',  # 全てのインターフェースでリッスン
            port=PORT,
            debug=False,     # プロダクション環境ではFalse
            threaded=True    # マルチスレッド対応
        )
    except Exception as e:
        logging.error(f"Server Error: {e}")

if __name__ == '__main__':
    main()



