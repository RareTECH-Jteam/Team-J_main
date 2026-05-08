        document.addEventListener("click", function(event) {
            if (!event.target.closest('.post-menu')) {
                document.querySelectorAll('.menu-dropdown').forEach(menu => {
                    menu.style.display = "none"
                })
            }
        })      
        
        function toggleMenu(postId){
            const elements = getElements(postId);
        
            // 再表示
            if(elements.menubutton.style.display == "none"){
                showElement(elements.menubutton);
                return;
            }
            
            // 非表示
            if(elements.menubutton.style.display =="block"){
                hideElement(elements.menubutton);
                return;
            }
        }

         // -- 編集ボタン押下時 --
        function enableEdit(postId){
            const elements = getElements(postId);
            
            // メニューを閉じる
            hideElement(elements.menubutton);

            // 投稿内容を非表示
            hideElement(elements.contentbody);

            // 編集エリアを表示
            showElement(elements.editarea);
        }

        // -- 保存ボタン --
        function saveEdit(postId){
            const elements = getElements(postId);
            const textarea = document.getElementById(`edit-content-${postId}`);

            // テキストエリアの値を取得
            const content = elements.edittextarea.value;
            const studytime = elements.editstudytime.value;

            // リクエスト(UPDATE)
            UpdateProcess(postId,content,studytime);
        }

        // flask側にリクエストを飛ばす
        function UpdateProcess(postId,content,studytime){
            const elements = getElements(postId);
            
            // csrfトークン取得
            const csrfToken = elements.csrfToken.value;
            
            // -- fetchリクエスト --
            fetch(`/posts/${postId}/update`,{
                method: "post",                                         // postリクエスト
                credentials:"same-origin",                              // 資格情報
                headers:{
                    "Content-Type" : "application/json",                // JSON形式で
                    "X-CSRF-Token" : `${csrfToken}`                     // csrfトークン設定
                },
                body:JSON.stringify({content:content,study_time:studytime})  // 投稿内容、勉強時間
            })
            .then(response => {
                // 成功時
                if(response.ok){
                    //ページをリロード
                    location.reload(); 
                }

                // 失敗時
                if(!response.ok){
                    location.href = `/posts/${postId}`
                }
            })
            .catch(error => {
                alert(error)
            })
        }
        
        // -- 編集キャンセル -- 
        function cancelEdit(postId){
            const elements = getElements(postId);
            
            // 編集エリア非表示
            hideElement(elements.editarea);
            
            // 投稿内容表示
            showElement(elements.contentbody);
        }


        function deletePost(postId){
            const elements = getElements(postId);
            
            // メニューを閉じる
            hideElement(elements.menubutton);

            // モーダルを開く前にエラーをリセット
            hideElement(elements.errormessage);

            // 削除確認モーダル 表示
            showElement(elements.deleteconfirm,"flex");

        }

        // -- 削除クリック -- 
        function confirmDelete(postId){
            const elements = getElements(postId);

            // リクエスト(DELETE)
            DeleteProcess(postId);
        }

        // flask側にリクエストを飛ばす
        function DeleteProcess(postId){
            const elements = getElements(postId);
            
            // csrfトークン取得
            const csrfToken = elements.csrfToken.value;
            
            // -- fetchリクエスト --
            fetch(`/posts/${postId}/delete`,{
                method: "post",                                         // postリクエスト
                credentials:"same-origin",                              // 資格情報
                headers:{
                    "Content-Type" : "application/json",                // JSON形式で
                    "X-CSRF-Token" : `${csrfToken}`                     // csrfトークン設定
                }
            })
            .then(async response => {
                // レスポンス取得
                const data = await response.json();
                
                // -- 成功 --
                if(response.ok){
                    // セッションストレージに成功メッセージ格納
                    sessionStorage.setItem('flashMessage', data.text);
                    location.reload(); //ページをリロード
                }
                // -- 失敗 --
                if(!response.ok){
                    
                    showElement(elements.errormessage);

                    // エラーメッセージ表示
                    elements.errormessage.textContent = data.text;
                }

            })
            .catch(error => {
                console.log(error);
                showElement(elements.errormessage);
            })
        }
        
        // -- エラーメッセージ表示 --
        function showErrors(){
            const elements = getElements();

        }
        // -- 削除キャンセル -- 
        function cancelDelete(postId){
            const elements = getElements(postId);

            // 削除エリア非表示、投稿内容表示
            hideElement(elements.deleteconfirm);
            showElement(elements.contentbody,"flex");
        }

        // -- 要素取得 --
        function getElements(postId) {
            return {
                toggle : document.getElementById("toggleMenu"),
                menubutton: document.getElementById(`menu-${postId}`),
                contentbody: document.getElementById(`post-detailbody-${postId}`),
                editarea : document.getElementById(`edit-area-${postId}`),
                edittextarea:document.getElementById(`edit-content-${postId}`),
                editstudytime:document.getElementById(`edit-study-time-input-${postId}`),
                deleteconfirm:document.getElementById(`deleteconfirm-${postId}`),
                errormessage:document.getElementById(`confirm_error_message-${postId}`),
                csrfToken:document.querySelector('input[name="csrf_token"]')
                }
        }

        // -- 表示 --
        function showElement(element, display = "block"){
            element.style.display = display;
        }

        // -- 再表示 --
        function hideElement(element){
            element.style.display = "none";
        }