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
    // reactionBtn: document.getElementById('add-reaction-btn'),
    pickerContainer: document.getElementById('picker-container'),
    reactionUserId: actionBar.dataset.reactionUserId,
    showEmojiArea :document.getElementById('showemoji')
}

function getCommentElements(commentId){
    return {
        commentmenu: document.getElementById(`comment-menu-${commentId}`),
        menubutton:document.getElementById(`menu-comment-${commentId}`),
        originalcontentbody:document.getElementById(`comment-body-${commentId}`),
        editarea: document.getElementById(`edit-area-${commentId}`),
        edittextarea: document.getElementById(`edit-comment-content-${commentId}`),
        showEmojiArea: document.getElementById(`showemoji-${commentId}`) 
    }
}

const state = {
    // リアクション
    postReactions: [],
    commentReactions: {}, // { commentId: [] }
    currentReactionType: 'post',
    currentReactionCommentId: null,
    
    // 編集
    editingType: null,
    editingCommentId: null,
}


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
/*  閉じる系操作        */
/************************/
// 編集・削除、絵文字ピッカーの要素外をクリックしても、閉じれるように

function closeAll() {
    
    // 編集・削除・絵文字ピッカーを閉じる
    closeAllMenus()
    
    // ツールチップ（誰がリアクションしたか）を削除
    document.querySelectorAll('.reaction-tooltip').forEach(tooltip => {
        tooltip.remove()
    })
    
    // ピッカーを閉じたときにホバー効果を元に戻す
    document.querySelector(".post-detail").classList.remove("picker-open");
}

// 全部閉じる処理（編集・削除・絵文字ピッカー）
function closeAllMenus() {
    document.querySelectorAll('.menu-dropdown, .menu-dropdown2').forEach(menu => {
        menu.style.display = "none";
    });
    elements.pickerContainer.style.display = "none";
}

// 枠外クリックで閉じる
document.addEventListener('click', function(e) {
    if (!e.target.closest('.action-bar') 
        && !e.target.closest('.action-bar-comment'
        && !e.target.closest('edit-post')
        )) {
        closeAll()
    }
});

// マウスが離れたら閉じる
document.querySelectorAll('.action-bar, .action-bar-comment').forEach(bar => {
    bar.addEventListener('mouseleave', function(e) {
       if(e.relatedTarget && e.relatedTarget.closest('.action-bar, .action-bar-comment')) return 
       
        closeAll()
    })
});




/************************/
/*  投稿編集機能        */
/************************/

// --  編集・削除メニューの表示、非表示を行う --
function toggleMenu(type,commentId=""){

    // 絵文字ピッカーを非表示にしておく
    elements.pickerContainer.style.display = "none";

    // 投稿かコメントかによって、取得するメニュー要素（編集・削除）を変える
    const target = type === 'post' 
        ? elements.menubutton 
        : getCommentElements(commentId).menubutton;
       
    // メニューが表示されていたら、閉じる
    if(target.style.display === "block"){
        hideElement(target)
        return
    }
    
    // メニューを表示
    showElement(target)
}

 // -- 編集ボタンクリック --
function enableEdit(type, commentId=""){
    
    // 状態管理設定
    state.editingType=type;
    state.editingCommentId = commentId;

    switch (type){
        case "post":
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

            break;

        case "comment":
             // コメント要素取得
             const commentElements = getCommentElements(commentId);
             
             // 編集開始時の値を保存
             commentElements.edittextarea.setAttribute('data-original-content'
                                                      , commentElements.edittextarea.value.trim())

            // トグルを非表示
            hideElement(commentElements.commentmenu);
            // メニューを閉じる
            hideElement(commentElements.menubutton);
            // 投稿内容を非表示
            hideElement(commentElements.originalcontentbody);

            // 編集エリアを表示
            showElement(commentElements.editarea);        
            
            break;
    }
}

// -- 編集保存ボタンクリック --
function saveEdit(){
    
    // 状態管理取得
    const type = state.editingType;
    const commentId = state.editingCommentId;

    let textarea;
    let content;
    let studytime;
    let body;
    
    switch(type){
        case "post":
            // 編集内容の値を取得
            content = elements.edittextarea.value;
            studytime = elements.editstudytime.value;
            
            // リクエストボディ
            body = {content:content,study_time:studytime};

            // 投稿内容アップデート
            UpdatePostContent(body);
            
            break;

       case "comment":
            const commentElements = getCommentElements(commentId);
            
            // 編集内容の値を取得
            content = commentElements.edittextarea.value;
            
            // リクエストボディ
            body = {content:content};

            // コメント内容アップデート
            UpdateCommentContent(body,commentId)
           
            break;
    }
}

// -- 投稿内容更新 --
async function UpdatePostContent(body){
    
    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;
    
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

// -- コメント内容更新 --
async function UpdateCommentContent(body,commentId){
    
    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;
    
    try{
        const {response, data} = await FetchRequest(`/posts/${postId}/comments/${commentId}/update`,"post",csrfToken,body)

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
    
    // 編集リセット
    resetEditArea();

}

// 編集キャンセル時のアクション
function resetEditArea() {
    
    // 状態管理取得
    const type = state.editingType;
    const commentId = state.editingCommentId;

    switch(type){
        case "post":
            // -- 編集内中に投稿が削除された時に復元する --
            elements.edittextarea.value = elements.edittextarea.getAttribute('data-original-content');
            elements.editstudytime.value = elements.editstudytime.getAttribute('data-original-studytime');

            // 編集エリア非表示
            hideElement(elements.editarea);

            // トグルのdiv全体を表示
            showElement(elements.postmenu, "flex");
            // 投稿内容表示
            showElement(elements.originalcontentbody);

            break;
        
        case "comment":
            const commentElements = getCommentElements(commentId);

            // -- 編集中にコメントが削除された時に復元する --
            commentElements.edittextarea.value = commentElements.edittextarea.getAttribute('data-original-content');

            // 編集エリア非表示
            hideElement(commentElements.editarea);

            // トグルのdiv全体を表示
            showElement(commentElements.commentmenu, "flex");
            
            // 投稿内容表示
            showElement(commentElements.originalcontentbody);    
            
            break;
    }

}

// -- 投稿削除 --
async function deletePost(type,commentId=""){
    
    // 状態管理設定
    state.editingType = type;
    state.editingId = commentId;

    switch(type){
        case "post":
            // メニューを閉じる
            hideElement(elements.menubutton);
           
            break;
        case "comment":
            const commentElements = getCommentElements(commentId);

           // メニューを閉じる
            hideElement(commentElements.menubutton);
           
            break;
    }

    
    const result = await showConfirm("確認","本当に削除しますか？","warning","削除");
    
    // 削除キャンセル時、何もしない
    if(!result.isConfirmed) return;

    // 投稿詳細削除
    if(type==="post"){

        DeletePostContent();
    }

    // コメント削除
    if(type === "comment"){
        
        DeleteCommentContent(commentId)
    }

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

// -- コメント削除 --
async function DeleteCommentContent(commentId){
    
    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;

    try{
        const {response, data} = await FetchRequest(`/posts/${postId}/comments/${commentId}/delete`,"post",csrfToken)


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
    state.postReactions = JSON.parse(elements.showEmojiArea.dataset.reactions);
    state.currentReactionType = "post";
    
    // リアクション表示
    updateReactionDisplay()       

    document.querySelectorAll('.reaction-area2').forEach(function(area){
        // data属性からコメントID取得
        const commentId = area.dataset.commentId;
        state.commentReactions[commentId] = JSON.parse(area.dataset.commentReactions) || [];
        
        // 状態を設定
        state.currentReactionType = "comment";
        state.currentReactionCommentId = commentId;
        
        // コメントごとにリアクション表示
        updateReactionDisplay()        
    })

    // 初期値に戻しておく
     state.currentReactionType = "post";
     state.currentReactionCommentId =null;
})

// -- 絵文字ピッカー表示するボタンのクリック時 --
document.querySelectorAll('.add-reaction-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        
        // 開いてたら閉じる
        if(elements.pickerContainer.style.display === "block") {
            hideElement(elements.pickerContainer)
            return
        }
        
        // メニューなど他のものを閉じる（ピッカーは除く）
        document.querySelectorAll('.menu-dropdown, .menu-dropdown2').forEach(menu => {
            menu.style.display = "none"
        })

           
        // 親要素を辿り、data属性から状態を取得する
        const bar = this.closest(".action-bar, .action-bar-comment");
        state.currentReactionType = bar.dataset.type || "post";
        state.currentReactionCommentId = bar.dataset.commentId || null;
        
        // クリックした要素の位置を取得する(絵文字ピッカーは重いので、使いまわすために表示をずらす)
        const rect = this.getBoundingClientRect();
        elements.pickerContainer.style.top = rect.bottom + 'px'
        elements.pickerContainer.style.left = rect.left + 'px'
        
        // 絵文字ピッカー表示
        showElement(elements.pickerContainer);

        // コメントの絵文字ピッカーにホバーした時に、投稿詳細のメニューが表示されるのを防ぐため
        document.querySelector('.post-detail').classList.add('picker-open')

        console.log(elements.pickerContainer.style.display) 
    })
})

// -- 投稿かコメントのリアクションかの状態を保存 --
function setReactionState(type, commentId=""){
    state.currentReactionType = type;
    state.currentReactionCommentId = commentId;
}

// settimeout設定変数
let reactionTimer = null;

// リアクション送信
async function sendReaction(emoji){

    // 状態取得
    type = state.currentReactionType;
    commentId = state.currentReactionCommentId;

    // 他のメニューなど開いてたら、閉じる
    closeAll();

    // csrfトークン取得
    const csrfToken = elements.csrfToken.value;

    // リクエストボディ
    const body = {emoji:emoji}

    // 連打された時の対策
    clearTimeout(reactionTimer)

    // 0.5秒後に実行する
    reactionTimer = setTimeout(async function (){
        
        try{
            let url ;

            // 投稿
            if(type === "post"){
                url = `/posts/${postId}/reactions`;
            }

            // コメント
            if(type === "comment"){
                url = `/posts/${postId}/comments/${commentId}/reactions`;
            }

            // レスポンス取得
            const {response, data} = await FetchRequest(url, "post",csrfToken, body)

            // data.reactions => [{'emoji':'👍', 'count':'3'} , {'emoji':'😂', 'count':'3'} ]
            
            // -- 成功 --
            if(response.ok){
                
                // 投稿
                if(type === "post"){
                    state.postReactions =data.reactions;
                }       
                
                // コメント
                if(type=== "comment"){
                    state.commentReactions[commentId] = data.reactions;
                }
                
                // リアクション表示
                updateReactionDisplay();
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

// -- リアクションされた絵文字の表示領域を生成 --
function createReactionElement(reactionLists,target){

    for(const reaction of reactionLists){
        // spanタグ生成
        const span = document.createElement('span');

        // クラス名設定
        span.className ="reaction-badge";

        // イベント設定(絵文字を直接クリックしても、反映されるように)
        span.addEventListener('click', function(){
            
            sendReaction(reaction.emoji,
                        state.currentReactionType,
                        state.currentReactionCommentId)
        })

        // マウス充てたとき、リアクションしたユーザー名を表示
        span.addEventListener('mouseover', function(){
            // ツールチップ取得
            const existing = span.querySelector('.reaction-tooltip')
            
            // 表示はマウス充てた時の1回だけにする
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

        // 自分のリアクションを目立たせるクラス
        if(reaction.reacted){
            span.classList.add("reacted");
        }else{
            span.classList.remove("reacted");
        }

        // 内容
        span.textContent = `${reaction.emoji} ${reaction.count}`

        // 絵文字表示エリアに追加
        target.appendChild(span);
    }    
}

// -- リアクションを画面に表示 --
function updateReactionDisplay(){
    
    const type = state.currentReactionType;
    
    const commentId = state.currentReactionCommentId;

    const target = type === "post"
                    ? elements.showEmojiArea
                    :getCommentElements(commentId).showEmojiArea

    const reactions = type === "post"
                    ? state.postReactions
                    : state.commentReactions[commentId] || []
    
    // 絵文字表示エリアを空で初期化
    target.innerHTML = "";

    const limit = 6

    // 先頭からlimitまでを抽出
    const displayReactions = reactions.slice(0, limit)

    // 折りたたみ解除ボタン 作成
    if(reactions.length > limit){
        createMoreBtn(target);
    }
    // リアクション要素生成
    createReactionElement(displayReactions,target);

    // …を追加
    if(reactions.length > limit){
        const more = document.createElement("span"); 
        more.textContent = "…";
        target.appendChild(more);
    }
}

// -- 折りたたみ解除ボタン生成 --
function createMoreBtn(target){
        const moreBtn = document.createElement("span");

        const reactions = state.currentReactionType === "post"
                        ? state.postReactions
                        : state.commentReactions[state.currentReactionCommentId] || []

        // クラス設定
        moreBtn.className ="reaction-more";
        
        // コンテント設定
        moreBtn.textContent = "＋";

        // イベント設定
        moreBtn.addEventListener("click",function(){
            // 折りたたみを解除して全件表示させる
            showAllReaction(reactions,target)
        })
        // 絵文字表示エリアに追加
        target.appendChild(moreBtn);
}

// -- リアクションすべて表示 --
function showAllReaction(reactionLists,target){
    target.innerHTML = "";

    // 折りたたむ
    const collapose = document.createElement("span");

    const reactions = state.currentReactionType === "post"
                    ? state.postReactions
                    : state.commentReactions[state.currentReactionCommentId] || []


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
    target.appendChild(collapose);

    // リアクション要素生成
    createReactionElement(reactions,target);
}

// -- サーバー通信 --
async function FetchRequest(url, method ,csrfToken, body=null) {
   
    // リクエストの設定
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


