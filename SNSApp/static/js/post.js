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

            // 元のテキストを保持
            elements.contentbody.setAttribute('data-original', elements.contentbody.innerHTML);
            const content = elements.contentbody.innerText;
            
            // HTML作成
            elements.contentbody.innerHTML = createEditArea(postId , content);

            // objに保存
            elements.textarea = document.getElementById(`edit-content-${postId}`)
            elements.saveBtn = document.getElementById(`save-btn-${postId}`)
        }

        function createEditArea(postId, content){
            return  `<section class="edit-post">
                        <div class="edit-post-body">
                            <textarea id="edit-content-${postId}" name="content">${content}</textarea> 
                            <div class="edit-post-footer">
                                <label class="edit-study-box">勉強時間：
                                    <input 
                                        type="text"
                                        name="study-time"
                                        inputmode="numeric" 
                                        pattern="[0-9]{1,3}"
                                        maxlength="3"
                                        value="0"
                                    >
                                    分
                                </label>
                                <button class="btn-primary" onclick="saveEdit('${postId}')">保存</button>
                                <button class="btn-primary" onclick="cancelEdit('${postId}')">キャンセル</button>
                            </div>
                        </div>
                    </section>`
        }

        // -- 保存ボタン --
        function saveEdit(postId){
            const textarea = document.getElementById(`edit-content-${postId}`);

            // テキストエリアの値を取得
            const content = textarea.value;

            // リクエスト
            UpdateProcess(postId,content);
        }

        function UpdateProcess(postId,content){
            const csrfToken = document.querySelector('input[name="csrf_token"]').value
            
            fetch(`/posts/${postId}/update`,{
                method: "post",
                credentials:"same-origin",
                headers:{
                    "Content-Type" : "application/json",
                    "X-CSRF-Token" : `${csrfToken}`
                },
                body:JSON.stringify({content:content,study_time:"80"})
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

            // 元のHTML情報取得
            const originalContent = elements.contentbody.getAttribute("data-original");
            
            elements.contentbody.innerHTML = originalContent;
        }


        function getElements(postId) {
            return {
                toggle : document.getElementById("toggleMenu"),
                menubutton: document.getElementById(`menu-${postId}`),
                contentbody: document.getElementById(`post-detalibody-${postId}`)
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