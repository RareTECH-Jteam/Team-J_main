        function getElements(postId) {
            return {
                toggle : document.getElementById("toggleMenu"),
                menubutton: document.getElementById(`menu-${postId}`),
                contentbody: document.getElementById(`post-detalibody-${postId}`)
                }
        }
        
        function toggleDisplay(element){
            // 再表示
            if(element.style.display == "none"){
                showElement(element);
                return;
            }
            
            // 非表示
            if(element.style.display =="block"){
                hideElement(element);
                return;
            }
        }

        // 表示
        function showElement(element){
            element.style.display = "block";
        }

        // 再表示
        function hideElement(element){
            element.style.display = "none";
        }

        function toggleMenu(postId){
            const elements = getElements(postId);
            
            toggleDisplay(elements.menubutton);
        }

        // 編集ボタン
        function enableEdit(postId){
            const elements = getElements(postId);
            
            // メニューを閉じる
            hideElement(elements.menubutton);

            // 元のテキストを保持
            elements.contentbody.setAttribute('data-original', elements.contentbody.innerHTML);
            const content = elements.contentbody.innerText;
            

        // HTML作成
        elements.contentbody.innerHTML = `
        <section class="edit-post">
            <div class="edit-post-body">
                <textarea name="content">${content}</textarea> 
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
        </section>
            `
        }

        function cancelEdit(postId){
            const elements = getElements(postId);

            // 元のHTML情報取得
            const originalContent = elements.contentbody.getAttribute("data-original");
            
            elements.contentbody.innerHTML = originalContent;
        }