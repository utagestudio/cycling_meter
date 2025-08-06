
function updateData() {
  fetch('/api/data')
    .then(response => response.json())
    .then(data => {
      document.getElementById('speed').textContent = data.speed;
      document.getElementById('distance').textContent = data.distance;
      document.getElementById('time').textContent = data.elapsed_time;
      document.getElementById('calories').textContent = data.calories;
      document.getElementById('last-update').textContent = new Date(data.last_update).toLocaleString('ja-JP');
      document.getElementById('status').textContent = 'オンライン';

      //cadence
      document.getElementById('cadence').textContent = parseInt(data.cadence).toFixed(1);
      const cadence_rate = data.cadence / 120 * 100;
        document.documentElement.style.setProperty('--cadence-rate', `${Math.min(cadence_rate, 100)}`);
    })
    .catch(error => {
      document.getElementById('status').textContent = 'エラー';
    });
}

function resetSession() {
  if (confirm('セッションをリセットしますか？')) {
    fetch('/api/reset', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          alert('セッションがリセットされました');
          // リセット後すぐにデータを更新
          updateData();
        } else {
          alert('リセットに失敗しました: ' + data.message);
        }
      })
      .catch(error => {
        console.error('リセットエラー:', error);
        alert('リセットに失敗しました');
      });
  }
}

// 1秒ごとにデータを更新
setInterval(updateData, 1000);

// 初回実行
updateData();