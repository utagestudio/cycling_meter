#!/bin/bash
# cycling_stop.sh
# エアロバイクシステム停止スクリプト

LOG_DIR="./log"
PID_DIR="./pid"

echo "=== エアロバイク システム停止 ==="
echo "時刻: $(date)"

# PIDファイルから各プロセスを停止
if [ -f "${PID_DIR}/cycling_calc.pid" ]; then
    CALC_PID=$(cat ./cycling_calc.pid)
    echo "データ計算プログラム (PID: $CALC_PID) を停止中..."
    kill $CALC_PID 2>/dev/null
    if kill -0 $CALC_PID 2>/dev/null; then
        sleep 2
        kill -9 $CALC_PID 2>/dev/null
    fi
    rm -f ./cycling_calc.pid
fi

if [ -f "${PID_DIR}/cycling_epd.pid" ]; then
    EPD_PID=$(cat ${PID_DIR}/cycling_epd.pid)
    echo "電子ペーパープログラム (PID: $EPD_PID) を停止中..."
    kill $EPD_PID 2>/dev/null
    if kill -0 $EPD_PID 2>/dev/null; then
        sleep 2
        kill -9 $EPD_PID 2>/dev/null
    fi
    rm -f ${PID_DIR}/cycling_epd.pid
fi

if [ -f "${PID_DIR}/cycling_web.pid" ]; then
    WEB_PID=$(cat ${PID_DIR}/cycling_web.pid)
    echo "Webサーバー (PID: $WEB_PID) を停止中..."
    kill $WEB_PID 2>/dev/null
    if kill -0 $WEB_PID 2>/dev/null; then
        sleep 2
        kill -9 $WEB_PID 2>/dev/null
    fi
    rm -f ${PID_DIR}/cycling_web.pid
fi

# プロセス名で検索して残っているものを停止
echo "残存プロセスをチェック中..."
pkill -f "cycling_calc.py"
pkill -f "cycling_epd.py"
pkill -f "cycling_server.py"

# データファイルの状態を表示
if [ -f "${LOG_DIR}/cycling_data.json" ]; then
    echo "データファイルの最終状態:"
    echo "  ファイル: ${LOG_DIR}/cycling_data.json"
    echo "  サイズ: $(ls -lh ${LOG_DIR}/cycling_data.json | awk '{print $5}')"
    echo "  最終更新: $(stat -c %y ${LOG_DIR}/cycling_data.json)"
fi

echo "=== 停止完了 ==="