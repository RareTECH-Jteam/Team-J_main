async function showConfirm(title,text,icon,confirmText="確認",cancelButtonText="キャンセル"){
    return await Swal.fire({
        title: title,
        html: text.replace(/\n/g, '<br/>'),
        icon: icon,
        width: 'min(90%,300px)',
        showCancelButton: true,
        customClass:'swal-text',        
        confirmButtonText: confirmText,
        cancelButtonText: cancelButtonText
    });
}


function showSuccess(message){
    Swal.fire({
        title: '成功',
        html: message.replace(/\n/g, '<br/>'),
        icon: 'success',
        width: 'min(90%,300px)',
        confirmButtonText: 'OK'
    });
}

function showError(message){
    Swal.fire({
        title: 'エラー',
        html: message.replace(/\n/g, '<br/>'),
        icon: 'error',
        width: 'min(90%,300px)',
        customClass:'swal-text',
        confirmButtonText: 'OK'
    });
}