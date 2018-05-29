/**
 * Created by taoyun on 2017/2/6.
 */

function onAjaxError (xhr, textStatus, error) {
    alert('Error: ' + textStatus);
}

function deleteUser(client) {
    if(confirm("确定要删除此用户吗？"))
    {
        $.ajax({
            url: "/delete_user",
            data: {
                client: client
            },
            method: 'POST',
            success: function(data) {
                console.log(data);
                if(data.success){
                    alert('删除成功');
                    window.location.reload();
                }
                else{
                    alert(data.lastlog);
                }
            },
            error: onAjaxError,
            dataType: 'json',
        });
    }
}

function downloadClient(client) {
    window.location.href = 'download_client?client=' + client;
}

function sendEmail(client) {
    $.ajax({
        url: "/send_email",
        data: {
            client: client
        },
        method: 'POST',
        success: function(data) {
            if(data.success){
                alert("操作成功，请注意查收邮件！");
                window.location.reload();
            }
            else{
                alert(data.lastlog);
            }
        },
        error: onAjaxError,
        dataType: 'json',
    });

}
