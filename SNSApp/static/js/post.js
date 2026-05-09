        // -- 要素取得 --
        function getElements(postId) {
            return {
                postmenu: document.getElementById(`post-menu-${postId}`),
                toggle : document.getElementById("toggleMenu"),
                menubutton: document.getElementById(`menu-${postId}`),
                originalcontentbody: document.getElementById(`post-detailbody-${postId}`),
                editarea : document.getElementById(`edit-area-${postId}`),
                editdErrormessage:document.getElementById(`edit_error_message-${postId}`),
                edittextarea:document.getElementById(`edit-content-${postId}`),
                editstudytime:document.getElementById(`edit-study-time-input-${postId}`),
                deleteconfirm:document.getElementById(`deleteconfirm-${postId}`),
                deleteErrormessage:document.getElementById(`confirm_error_message-${postId}`),
                csrfToken:document.querySelector('input[name="csrf_token"]')
                }
        }

        document.addEventListener("click", function(event) {
            // トグルと編集エリア以外の枠外をクリックしたとき
            if (!event.target.closest('.post-menu')) {
                // メニューを閉じる
                document.querySelectorAll('.menu-dropdown').forEach(menu => {
                    menu.style.display = "none";
                });
            }
        });
        
        function toggleMenu(postId){
            const elements = getElements(postId);
        
            // モーダルを開く前にエラーをリセット
            hideVisibility(elements.editdErrormessage);

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
        async function UpdateProcess(postId,content,studytime){
            const elements = getElements(postId);
            
            // csrfトークン取得
            const csrfToken = elements.csrfToken.value;

            const body = {content:content,study_time:studytime}

            try{
                const {response, data} = await postRequest(`/posts/${postId}/update`,csrfToken,body)


                // -- 成功 --
                if(response.ok){
                    location.reload();
                }
                
                // -- 失敗 --
                if(!response.ok){
                    console.log(data);
                    // エラーメッセージ表示
                    showVisibility(elements.editdErrormessage);
                    elements.editdErrormessage.textContent = data.text;
                }


            }catch(error){
                console.log(error);
                showVisibility(elements.editdErrormessage);
            }
        }
        
        // -- 編集キャンセル -- 
        function cancelEdit(postId){
            const elements = getElements(postId);
        
            resetEditArea(postId);
        }

        function resetEditArea(postId) {
            const elements = getElements(postId)

            // -- 編集内容上で投稿内容が削除された時に復元する --
            elements.edittextarea.value = elements.edittextarea.getAttribute('data-original-content');
            elements.editstudytime.value = elements.editstudytime.getAttribute('data-original-studytime');

            // モーダルを開く前にエラーをリセット
            hideVisibility(elements.editdErrormessage);

            // 編集エリア非表示
            hideElement(elements.editarea);

            // トグルのdiv全体を非表示
            showElement(elements.postmenu, "flex");
            // 投稿内容表示
            showElement(elements.originalcontentbody);
        }



        function deletePost(postId){
            const elements = getElements(postId);
            
            // メニューを閉じる
            hideElement(elements.menubutton);

            // モーダルを開く前にエラーをリセット
            hideElement(elements.deleteErrormessage);

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
        async function DeleteProcess(postId){
            const elements = getElements(postId);
            
            // csrfトークン取得
            const csrfToken = elements.csrfToken.value;

            try{
                const {response, data} = await postRequest(`/posts/${postId}/delete`,csrfToken)


                // -- 成功 --
                if(response.ok){
                    location.reload();
                }
                
                // -- 失敗 --
                if(!response.ok){
                    
                    // エラーメッセージ表示
                    showElement(elements.deleteErrormessage);
                    elements.deleteErrormessage.textContent = data.text;
                }


            }catch(error){
                console.log(error);
                showElement(elements.deleteErrormessage);
            }
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
            showElement(elements.originalcontentbody,"flex");
        }

        // -- POSTリクエスト --
        async function postRequest(url, csrfToken, body=null) {
            const options ={
                method: "post",                                         // postリクエスト
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