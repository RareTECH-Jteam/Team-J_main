const countDown = document.getElementById('countDown');

// カウントダウンがある場合（バトンが送られているときに表示される）
if (countDown){
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
        const seconds = Math.floor(totalSeconds % 60);

        countDown.textContent = `///締め切りまであと ${String(hours).padStart(2, '0')}:${String(minuts).padStart(2,'0')}:${String(seconds).padStart(2,'0')}///`;

        if(distanse < 0){
            clearInterval(interval);
            location.reload();
        }
    }

    // 1秒ごとに更新
    const interval = setInterval(updateCountDown,1000);

    // 初回読み込み時
    updateCountDown();
}

// ページが読み込まれた時
document.addEventListener('DOMContentLoaded', function(){

    const form = document.querySelector('.new-task-main');
    const btn = document.querySelector('.send-task-btn');

    form.addEventListener('submit', async function(e){
        // ボタン押下されても、postされないようにする
        // 遷移されると、通知が届かないため
        e.preventDefault();

        const result = await showConfirm("確認","このバトンを次の人に送りますか？","question","送る")

        // キャンセルされた場合 何もしない
        if(!result.isConfirmed) return;

        postBaton(form);

    })
})

// バトン送る
async function postBaton(form){

    try{
        const formData = new FormData(form);

        const result = await fetch("/baton/send"
            ,{  method:"POST"
                , body: formData
            });

        const data = await result.json();
        
        // 失敗
        if(!result.ok){
            showError(data.text);
        }        

    }catch(error){
        showError("通信エラーが発生しました。");
    }
}
