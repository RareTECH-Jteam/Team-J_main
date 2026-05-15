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

function showError(message){
    Swal.fire({
        title: 'エラー',
        text: message,
        icon: 'error',
        width: 'min(90%,300px)',
        confirmButtonText: 'OK'
    });
}