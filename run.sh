#!/bin/bash
# run.sh
# エアロバイクシステム起動スクリプト

SCRIPT_DIR="./src"
LOG_DIR="./log"

echo "=== エアロバイク システム起動 ==="
echo "時刻: $(date)"
echo "ディレクトリ: $SCRIPT_DIR"
echo

# 既存のプロセスを確認・停止
echo "既存プロセスのチェック..."
pkill -f "cycling_calc.py"
pkill -f "cycling_epd.py" 
pkill -f "cycling_server.py"
pkill -f "shutdown_button.py"
sleep 2

# ログファイルをクリア
echo "ログファイルの初期化..."
> ${LOG_DIR}/cycling_calc.log
> ${LOG_DIR}/cycling_epd.log
> ${LOG_DIR}/cycling_web.log

# データファイルの存在確認
if [ -f "${LOG_DIR}/cycling_data.json" ]; then
    echo "既存データファイルが見つかりました"
    echo "内容: $(cat ${LOG_DIR}/cycling_data.json | head -1)"
else
    echo "新規セッションを開始します"
fi

echo

cd $SCRIPT_DIR

# 1. データ計算プログラムを開始
echo "データ計算プログラムを開始..."
python3 cycling_calc.py &
CALC_PID=$!
echo "データ計算プログラム PID: $CALC_PID"

# 2秒待機
sleep 2

# 2. 電子ペーパー表示プログラムを開始
echo "電子ペーパー表示プログラムを開始..."
python3 cycling_epd.py &
EPD_PID=$!
echo "電子ペーパープログラム PID: $EPD_PID"

# 2秒待機
sleep 2

# 3. Webサーバーを開始
echo "Webサーバーを開始..."
python3 cycling_server.py &
WEB_PID=$!
echo "Webサーバー PID: $WEB_PID"

# 4. シャットダウンボタン監視を開始
echo "シャットダウンボタン監視を開始..."
python3 shutdown_button.py &
SHUTDOWN_PID=$!
echo "シャットダウンボタン PID: $SHUTDOWN_PID"

echo
echo "=== 起動完了 ==="
echo "データ計算: PID $CALC_PID"
echo "電子ペーパー: PID $EPD_PID" 
echo "Webサーバー: PID $WEB_PID"
echo "シャットダウンボタン: PID $SHUTDOWN_PID"
echo
echo "アクセス方法:"
echo "  ローカル: http://localhost:5000"
echo
echo "停止方法:"
echo "  ./stop.sh"

# PIDファイルに保存
cd ..
mkdir -p pid
echo "$CALC_PID" > ./pid/cycling_calc.pid
echo "$EPD_PID" > ./pid/cycling_epd.pid
echo "$WEB_PID" > ./pid/cycling_web.pid
echo "$SHUTDOWN_PID" > ./pid/shutdown_button.pid

# プロセス監視ループ
echo
echo "プロセス監視を開始します..."