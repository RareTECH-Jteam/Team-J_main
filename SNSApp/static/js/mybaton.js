const countDown = document.getElementById('countDown');
const timeLimit = new Date(countDown.dataset.taskLimit).getTime();

function updateCountDown(){
    const now = new Date();
    
    // 現時刻とタイムリミットの差分
    const distanse = timeLimit - now;

    // 秒に換算
    const totalSeconds = Math.floor(distanse / 1000);

    // 時
    const hours = Math.floor(totalSeconds / 3600);

    // 分
    const minuts = Math.floor(totalSeconds % 3600 / 60);
    
    // 秒
    const seconds = totalSeconds % 60;

    countDown.textContent = `★締め切りまであと ${String(hours).padStart(2, '0')}:${String(minuts).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;

    if(distanse < 0){
        clearInterval(interval);
        location.reload();
    }
}

// 1秒ごとに更新
const interval = setInterval(updateCountDown,1000);

// 初回読み込み時
updateCountDown();