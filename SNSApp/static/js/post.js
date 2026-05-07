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

            // 投稿内容を非表示、編集エリアを表示
            hideElement(elements.contentbody);
            showElement(elements.editarea);
        }

        // -- 保存ボタン --
        function saveEdit(postId){
            const elements = getElements(postId);
            const textarea = document.getElementById(`edit-content-${postId}`);

            // テキストエリアの値を取得
            const content = elements.edittextarea.value;

            // リクエスト
            UpdateProcess(postId,content);
        }

        // flask側にリクエストを飛ばす
        function UpdateProcess(postId,content){
            const elements = getElements(postId);
            
            // csrfトークン取得
            const csrfToken = elements.csrfToken.value
            
            
            // -- fetchリクエスト --
            fetch(`/posts/${postId}/update`,{
                method: "post",                                         // postリクエスト
                credentials:"same-origin",                              // 資格情報
                headers:{
                    "Content-Type" : "application/json",                // JSON形式で
                    "X-CSRF-Token" : `${csrfToken}`                     // csrfトークン設定
                },
                body:JSON.stringify({content:content,study_time:"80"})  // 投稿内容、勉強時間
            })
            .then(response => {
                if(response.ok){
                    location.reload(); //ページをリロード
                }
                else{
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
            
            // 編集エリア非表示、投稿内容表示
            hideElement(elements.editarea);
            showElement(elements.contentbody);
        }


        function getElements(postId) {
            return {
                toggle : document.getElementById("toggleMenu"),
                menubutton: document.getElementById(`menu-${postId}`),
                contentbody: document.getElementById(`post-detailbody-${postId}`),
                editarea : document.getElementById(`edit-area-${postId}`),
                edittextarea:document.getElementById(`edit-content-${postId}`),
                csrfToken:document.querySelector('input[name="csrf_token"]')
                }
        }

        // -- 表示 --
        function showElement(element){
            element.style.display = "block";
        }

        // -- 再表示 --
        function hideElement(element){
            element.style.display = "none";
        }