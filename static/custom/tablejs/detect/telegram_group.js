$(function () {
    operate.operateInit();
});

// 全局变量
window.modal_results = document.getElementById("OperateRestartresults");
window.modal_footer = document.getElementById("progressFooter");
window.modal_head = document.getElementById("progress_head");

//升级所用到的全局变量
window.upgrade_postData = {};

//操作
var operate = {
    //初始化按钮事件
    operateInit: function () {
        this.DisplayPanel();
        //this.Getform();
        //this.Submit();
        //this.showSelectedValue();
        //this.Exe();
    },

    DisplayPanel: function (){
        $("#command_panel").bind('click',function () {
            that = document.getElementById("command_form")
            if (that.style.display == "none"){
                that.style.display = "inline";
                document.getElementById('command_panel').innerHTML = "-";
                document.getElementById('command_panel').title = "隐藏";
            }else {
                that.style.display = "none";
                document.getElementById('command_panel').innerHTML = "+";
                document.getElementById('command_panel').title = "展开";
            }
        });
    },

    Submit: function(submit){
        // 获取要发送信息的群组
        group = public.showSelectedValue('telegram_group', false)
        // console.log(group)
        if (group.length == 0 ){
            alert('请选择对应的telegram群组！');
            return false;
        }

        // 获取要@的部门或者组
        atUsers = public.showSelectedValue('telegram_atusers', false)
        // console.log(atUsers)

        // 获取信息文本
        text = document.getElementById('textarea_telegram_text').value
        // console.log(text)

        if (text.length == 0){
            alert('信息不能为空！');
            return false;
        }

        var postData = {
            'group':   group,
            'atUsers': atUsers,
            'text':    text
        }

        $('#runprogress').modal('show');
        modal_results.innerHTML = "";
        modal_footer.innerHTML = "";
        $("#progress_bar").css("width", "30%");
        modal_head.innerHTML = "操作进行中，请勿刷新页面......";

        $.ajax({
            url: "/message/telegram/sendgroupmessage",
            type: "post",
            data: JSON.stringify(postData),
            success: function (data, status) {
                if (status == 1){
                    toastr.success(data);
                }else {
                    toastr.warning(data);
                }
                modal_head.innerHTML = "执行完成...";
                $("#progress_bar").css("width", "100%");
                $('#OperateRestartresults').append('<p>执行完成......</p>' );
                //console.log('websocket已关闭');
                setTimeout(function(){$('#runprogress').modal('hide');}, 1000);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                if (XMLHttpRequest.status == 0){
                    toastr.error('后端服务不响应', '错误')
                }else {
                    toastr.error(XMLHttpRequest.responseText, XMLHttpRequest.status)
                }
                modal_head.innerHTML = "与服务器连接失败...";
                $('#OperateRestartresults').append('<p>连接失败......</p>' );
                setTimeout(function(){$('#runprogress').modal('hide');}, 1000);

                //console.info(XMLHttpRequest)
                //alert(XMLHttpRequest.status+': '+XMLHttpRequest.responseText);
                //tableInit.myViewModel.refresh();
            }
        });

        return false;
    },

};