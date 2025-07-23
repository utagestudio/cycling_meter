from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)

def load_cycling_data():
    logging.info("load data")
    data_file = './cycling_data.json'
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.info(f"data load error: {e}")

    return {
        'speed': 0.0,
        'distance': 0.0,
        'elapsed_time': '0:00:00',
        'calories': 0.0,
        'cadence': 0.0,
        'last_update': datatime.now().isoformat()
    }

@app.route('/')
def index():
    """ main page """
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """ return data from API """
    data = load_cycling_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



