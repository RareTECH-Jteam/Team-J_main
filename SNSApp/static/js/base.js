async function showConfirm(title,text,icon,confirmText="確認",cancelButtonText="キャンセル"){
    return await Swal.fire({
        title: title,
        text: text,
        icon: icon,
        width: 'min(90%,300px)',
        showCancelButton: true,
        confirmButtonText: confirmText,
        cancelButtonText: cancelButtonText
    });
}


function showSuccess(message){
    Swal.fire({
        title: '成功',
        text: message,
        icon: 'success',
        width: 'min(90%,300px)',
        confirmButtonText: 'OK'
    });
}

function showError(message){
    Swal.fire({
        title: 'エラー',
        text: message,
        icon: 'error',
        width: 'min(90%,300px)',
        confirmButtonText: 'OK'
    });
}