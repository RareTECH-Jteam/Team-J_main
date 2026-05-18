/************************/
/*  初期化処理          */
/************************/

// postIdはHTMLから取得
const actionBar = document.querySelector('.action-bar');
const postId = actionBar.dataset.postid;

// 全要素を一度に取得
const elements = {
    postmenu: document.getElementById(`post-menu-${postId}`),
    menubutton: document.getElementById(`menu-${postId}`),
    originalcontentbody: document.getElementById(`post-detailbody-${postId}`),
    editarea: document.getElementById(`edit-area-${postId}`),
    edittextarea: document.getElementById(`edit-content-${postId}`),
    editstudytime: document.getElementById(`edit-study-time-input-${postId}`),
    csrfToken: document.querySelector('input[name="csrf_token"]'),
    reactionBtn: document.getElementById('add-reaction-btn'),
    pickerContainer: document.getElementById('picker-container'),
    reactionUserId: actionBar.dataset.reactionUserId,
    showEmojiArea :document.getElementById('showemoji')
}

// リアクションを格納する
let reactions = []

// ピッカーを作る
// プレビュー(preview)と検索(search)を非表示に設定
const pickerOptions = { 
    onEmojiSelect: function(emoji){
        sendReaction(emoji.native)
    },
    locale : "ja",
    previewPosition:"none",
    skinTonePosition:"preview",
    navPosition: "bottom"
}

const picker = new EmojiMart.Picker(pickerOptions)

// ピッカー要素追加
elements.pickerContainer.appendChild(picker);


/************************/
/*  投稿編集機能        */
/************************/

// 編集・削除、絵文字ピッカーの要素外をクリックしても、閉じれるように
document.addEventListener('click', function(e) {
    if (!e.target.closest('.action-bar')) {
        document.querySelectorAll('.menu-dropdown').forEach(menu => {
            menu.style.display = "none";
        });
        elements.pickerContainer.style.display = "none";
    }
});

document.querySelector('.action-bar').addEventListener('mouseleave', function() {
    document.querySelectorAll('.menu-dropdown').forEach(menu => {
        menu.style.display = "none";
    });
    elements.pickerContainer.style.display = "none";
});

// トグルメニュークリック
function toggleMenu(){

    // 絵文字ピッカーを非表示にしておく
    elements.pickerContainer.style.display = "none";

    // トグルメニュー 再表示
    if(elements.menubutton.style.display == "none"){
        showElement(elements.menubutton);
        return;
    }
    
    // トグルメニュー 非表示
    if(elements.menubutton.style.display =="block"){
        hideElement(elements.menubutton);
        return;
    }
}

 // -- 編集ボタンクリック --
function enableEdit(){

    // 編集開始時の値を保存
    elements.edittextarea.setAttribute('data-original-content', elements.edittextarea.value.trim())
    elements.editstudytime.setAttribute('data-original-studytime', elements.editstudytime.value)

    // トグルを非表示
    hideElement(elements.postmenu);
    // メニューを閉じる
    hideElement(elements.menubutton);
    // 投稿内容を非表示
    hideElement(elements.originalcontentbody);

    // 編集エリアを表示
    showElement(elements.editarea);
}

// -- 編集保存ボタンクリック --
function saveEdit(){
    const textarea = document.getElementById(`edit-content-${postId}`);

    // テキストエリアの値を取得
    const content = elements.edittextarea.value;
    const studytime = elements.editstudytime.value;

    // リクエスト(UPDATE)
    UpdatePostContent(content,studytime);
}

// -- 投稿内容更新 --
async function UpdatePostContent(content,studytime){
    
    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;

    const body = {content:content,study_time:studytime}

    try{
        const {response, data} = await FetchRequest(`/posts/${postId}/update`,"post",csrfToken,body)


        // -- 成功 --
        if(response.ok){
            location.reload();
        }
        
        // -- 失敗 --
        if(!response.ok){
            console.log(data);
            
            // エラーメッセージ表示
            showError(data.text);
        }


    }catch(error){
        console.log(error);

        showError("編集に失敗しました");
    }
}

// -- 編集キャンセルボタンクリック -- 
function cancelEdit(){

    resetEditArea();
}

function resetEditArea() {

    // -- 編集内容上で投稿内容が削除された時に復元する --
    elements.edittextarea.value = elements.edittextarea.getAttribute('data-original-content');
    elements.editstudytime.value = elements.editstudytime.getAttribute('data-original-studytime');

    // 編集エリア非表示
    hideElement(elements.editarea);

    // トグルのdiv全体を非表示
    showElement(elements.postmenu, "flex");
    // 投稿内容表示
    showElement(elements.originalcontentbody);
}

// -- 投稿削除 --
async function deletePost(){
    
    // メニューを閉じる
    hideElement(elements.menubutton);

    const result = await showConfirm("確認","本当に削除しますか？","warning","削除");

    if(!result.isConfirmed) return;


    DeletePostContent();

}

// -- 投稿内容削除 --
async function DeletePostContent(){
    
    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;

    try{
        const {response, data} = await FetchRequest(`/posts/${postId}/delete`,"post",csrfToken)


        // -- 成功 --
        if(response.ok){
            location.reload();
        }
        
        // -- 失敗 --
        if(!response.ok){
            
            // エラーメッセージ表示
            showError(data.text);
        }


    }catch(error){
        console.log(error);
        // showElement(elements.deleteErrormessage);

        showError("削除に失敗しました");
    }
}


/************************/
/*  リアクション機能    */
/************************/

// -- ロードイベント --
document.addEventListener('DOMContentLoaded', function(){

    console.log(elements.showEmojiArea.dataset.reactions);

    // 初回はHTML側に埋め込まれてるリアクション情報を取得
    reactions = JSON.parse(elements.showEmojiArea.dataset.reactions);

    // リアクション表示
    updateReactionDisplay()
})


// -- 絵文字ピッカー表示 --
elements.reactionBtn.addEventListener('click', function(){
    
    // 非表示
    if (elements.pickerContainer.style.display === "block") {
        hideElement(elements.pickerContainer)
    } 
    
    // 表示
    if(elements.pickerContainer.style.display != "block"){
        
        closeAll();
        
        showElement(elements.pickerContainer);
    }
});

// 全部閉じる処理
function closeAll() {
    elements.pickerContainer.style.display = "none";
    
    document.querySelectorAll('.menu-dropdown').forEach(menu => {
        menu.style.display = "none";
    });

     // ツールチップも閉じる
    document.querySelectorAll('.reaction-tooltip').forEach(tooltip => {
        tooltip.remove()
    })
}
 

let reactionTimer = null;
// リアクション送信
async function sendReaction(emoji){
    
    // 他のメニューなど開いてたら、閉じる
    closeAll();

    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;

    const body = {emoji:emoji}

    // 連打された時の対策
    clearTimeout(reactionTimer)

    // 0.5秒後に実行する
    reactionTimer = setTimeout(async function (){
        
        try{
            // レスポンス取得
            const {response, data} = await FetchRequest(`/posts/${postId}/reactions`, "post",csrfToken, body)

            // data.reactions => [{'emoji':'👍', 'count':'3'} , {'emoji':'😂', 'count':'3'} ]
            
            // -- 成功 --
            if(response.ok){
                console.log(data.reactions)

            reactions = data.reactions;

            updateReactionDisplay()
            }
            
            // -- 失敗 --
            if(!response.ok){
                
                // エラーメッセージ表示
                showError(data.text);
            }

        }catch(error){
            console.log(error);

            showError("リアクションに失敗しました");
        }
    },500)
}

function createReactionElement(reactionLists){
    
    for(const reaction of reactionLists){
        // spanタグ生成
        const span = document.createElement('span');

        // クラス名設定
        span.className ="reaction-badge";

        // イベント設定
        span.addEventListener('click', function(){
            sendReaction(reaction.emoji)
        })

        // マウス充てたとき、リアクションしたユーザー名を表示
        span.addEventListener('mouseover', function(){
            // ツールチップ取得
            const existing = span.querySelector('.reaction-tooltip')
            
            // 既に存在してたら 削除
            if(existing){
                span.removeChild(existing);
            } 
            
            // ツールチップ作成
            const tooltip = document.createElement('div');
            tooltip.className = "reaction-tooltip";
            tooltip.textContent = reaction.users.join("\r\n");
            span.appendChild(tooltip);
        })

        // マウス離したとき
        span.addEventListener('mouseleave', function(){
            const tooltip = document.querySelector('.reaction-tooltip');
            if(tooltip) span.removeChild(tooltip); 
        })        

        // 内容
        span.textContent = `${reaction.emoji} ${reaction.count}`

        // 絵文字表示エリアに追加
        elements.showEmojiArea.appendChild(span);
    }    
}

// -- リアクションを画面に表示 --
function updateReactionDisplay(){
    // 絵文字表示エリアを空で初期化
    elements.showEmojiArea.innerHTML = "";

    const limit = 6

    // 先頭からlimitまでを抽出
    const displayReactions = reactions.slice(0, limit)

    // 折りたたみ解除ボタン 作成
    if(reactions.length > limit){
        createMoreBtn();
    }
    // リアクション要素生成
    createReactionElement(displayReactions);

    // …を追加
    if(reactions.length > limit){
        const more = document.createElement("span"); 
        more.textContent = "…";
        elements.showEmojiArea.appendChild(more);
    }
}

// -- 折りたたみ解除ボタン生成 --
function createMoreBtn(){
        const moreBtn = document.createElement("span");

        // クラス設定
        moreBtn.className ="reaction-more";
        
        // コンテント設定
        moreBtn.textContent = "＋";

        // イベント設定
        moreBtn.addEventListener("click",function(){
            // 折りたたみを解除して全件表示させる
            showAllReaction(reactions)
        })
        // 絵文字表示エリアに追加
        elements.showEmojiArea.appendChild(moreBtn);
}

// -- リアクションすべて表示 --
function showAllReaction(reactionLists){
    elements.showEmojiArea.innerHTML = "";

    // 折りたたむ
    const collapose = document.createElement("span");

    // クラス設定
    collapose.className ="reaction-more";

    // 折りたたみ
    collapose.textContent = "－";

    // イベント設定
    collapose.addEventListener("click", function(){
        
        // 表示を元に戻す
        updateReactionDisplay();
    })

    // 折りたたみを追加
    elements.showEmojiArea.appendChild(collapose);

    // リアクション要素生成
    createReactionElement(reactions);
}

// -- サーバー通信 --
async function FetchRequest(url, method ,csrfToken, body=null) {
    const options ={
        method: method,                                         // postリクエスト
        credentials:"same-origin",                              // 資格情報
        headers:{
            "Content-Type" : "application/json",                // JSON形式で
            "X-CSRF-Token" : `${csrfToken}`                     // csrfトークン設定
        }                
    }
    // bodyがある場合のみ
    if(body){
        options.body = JSON.stringify(body);
    }

    console.log("fetchオプション:", options); // bodyキーがあるか確認

    const response =  await fetch(url,options)
    const data = await response.json();

    return {response, data};   
}

// -- 表示 --
function showElement(element, display = "block"){
    element.style.display = display;
}

// -- 再表示 --
function hideElement(element){
    element.style.display = "none";
}

// -- エラーメッセージ用 (高さそのまま確保) --
function hideVisibility(element){
    element.style.visibility = "hidden";
}

function showVisibility(element){
    element.style.visibility = "visible";
}        


