    const isMobile = window.innerWidth <= 480;
    const socket = io();
    const notyf = new Notyf({
        duration: 5000,
        dismissible: true,
        position: {
            x: isMobile ? 'left' : 'center',
            y: 'top'
        },        
        types: [
            {
                type: 'info',
                background: '#F7F7F8',  
                className: 'notyf-custom',
                icon: {
                    tagName: 'i',
                    className: 'baton-icon_notf',
                    text: '', // imgタグなのでテキストは空
                }
            }
        ]
    });

    socket.on('connect', function() {
        // 接続完了後にサーバーに未読確認を依頼
        //socket.emit('check_unread');
    });


    // サーバーからお知らせがあったら、表示する
    socket.on('notification', function(data) {
        notyf.open({type: 'info', message: data.message});
        console.log(data);
        if (data.reload){
            location.reload();
        }

        // 文字列ではなく、オブジェクトとして送る
        socket.emit('notification_received', {
            baton_id: data.baton_id
        });
    });
