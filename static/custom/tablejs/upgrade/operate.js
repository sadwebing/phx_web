$(function () {
    operate.operateInit();
});

//全局变量
window.modal_results = document.getElementById("OperateRestartresults");
window.modal_footer = document.getElementById("progressFooter");
window.modal_head = document.getElementById("progress_head");

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

        $("#command2_panel").bind('click',function () {
            that = document.getElementById("command2_form")
            if (that.style.display == "none"){
                that.style.display = "inline";
                document.getElementById('command2_panel').innerHTML = "-";
                document.getElementById('command2_panel').title = "隐藏";
            }else {
                that.style.display = "none";
                document.getElementById('command2_panel').innerHTML = "+";
                document.getElementById('command2_panel').title = "展开";
            }
        });

        $("#restart_panel").bind('click',function () {
            that = document.getElementById("restart_form")
            if (that.style.display == "none"){
                that.style.display = "inline";
                document.getElementById('restart_panel').innerHTML = "-";
                document.getElementById('restart_panel').title = "隐藏";
            }else {
                that.style.display = "none";
                document.getElementById('restart_panel').innerHTML = "+";
                document.getElementById('restart_panel').title = "展开";
            }
        });
    },
    
    GetProjectProd: function (){
        var envir = public.showSelectedValue('project_envir'); //获取选中的产品环境
        //console.log(envir);

        if (envir.length != 1){
            alert('产品环境选择错误！');
            return false;
        }

        var productHtml = "";

        for (var i = 0; i < items.length; i++){
            //console.log(envir[0]);
            //console.log(items[i]['envir'][0]);
            if (items[i]['envir'][0] ==  envir[0]){
                productHtml = productHtml + "<option value="+items[i]['product'][0]+">"+items[i]['product'][1]+"</option>";
            };
        }

        document.getElementById("project_product").innerHTML=productHtml;
        $('.selectpicker').selectpicker('refresh');
    },

    GetProjectCust: function (){
        var envir = public.showSelectedValue('project_envir'); //获取选中的产品环境
        var product = public.showSelectedValue('project_product'); //获取选中的产品
        //console.log(envir);

        if (envir.length != 1){
            alert('产品环境选择错误！');
            return false;
        }

        if (product.length != 1){
            alert('产品选择错误！');
            return false;
        }

        var customerHtml = "";

        for (var i = 0; i < items.length; i++){
            //console.log(envir[0]);
            //console.log(items[i]['envir'][0]);
            if (items[i]['envir'][0] ==  envir[0] && items[i]['product'][0] == product[0]){
                customerHtml = customerHtml + "<option value="+items[i]['customer'][0]+">"+items[i]['customer'][1]+"</option>";
            };
        }

        document.getElementById("project_customer").innerHTML=customerHtml;
        $('.selectpicker').selectpicker('refresh');
    },

    GetProjectcodeEnv: function (){
        var envir = public.showSelectedValue('project_envir'); //获取选中的产品环境
        var product = public.showSelectedValue('project_product'); //获取选中的产品
        var customer = public.showSelectedValue('project_customer'); //获取选中的客户

        if (envir.length != 1){
            alert('产品环境选择错误！');
            return false;
        }

        if (product.length != 1){
            alert('产品选择错误！');
            return false;
        }

        if (customer.length != 1){
            alert('客户选择错误！');
            return false;
        }

        var codeEnvHtml = "";

        for (var i = 0; i < items.length; i++){
            //console.log(envir[0]);
            //console.log(items[i]['envir'][0]);
            if (items[i]['envir'][0] ==  envir[0] && items[i]['product'][0] == product[0] && items[i]['customer'][0] == customer[0]){
                if (items[i]['svn_master']['gray_env'].length > 0) {
                    codeEnvHtml = codeEnvHtml + "<option value=gray_env>代码-灰度环境</option>";
                }
                if (items[i]['svn_master']['online_env'].length > 0) {
                    codeEnvHtml = codeEnvHtml + "<option value=online_env>代码-运营环境</option>";
                }
            };
        }

        document.getElementById("project_codeEnv").innerHTML=codeEnvHtml;
        $('.selectpicker').selectpicker('refresh');
    },

    Submit: function(submit){
        var postData = {
            'envir': public.showSelectedValue('project_envir', false), //获取选中的产品环境
            'product': public.showSelectedValue('project_product', false), //获取选中的产品
            'customer': public.showSelectedValue('project_customer', false), //获取选中的客户
            'codeEnv': public.showSelectedValue('project_codeEnv', false), //获取选中的代码环境
            'items': items,
        }

        if (postData['envir'].length != 1){
            alert('产品环境选择错误！');
            return false;
        }

        if (postData['product'].length != 1){
            alert('产品选择错误！');
            return false;
        }

        if (postData['customer'].length != 1){
            alert('客户选择错误！');
            return false;
        }

        if (postData['codeEnv'].length != 1){
            alert('代码环境选择错误！');
            return false;
        }

        for (var i = 0; i < items.length; i++){
            if (items[i]['envir'][0] ==  postData['envir'][0] && items[i]['product'][0] == postData['product'][0] && items[i]['customer'][0] == postData['customer'][0]){
                postData['cmd'] = items[i]['svn_master'][postData['codeEnv']];
                postData['minion_id'] = items[i]['svn_master']['minion_id'];
                postData['id'] = items[i]['id'];
            };
        }

        //alert("获取到的表单数据为:"+JSON.stringify(postData));
        $('#runprogress').modal('show');
        modal_results.innerHTML = "";
        modal_footer.innerHTML = "";
        $("#progress_bar").css("width", "30%");
        modal_head.innerHTML = "操作进行中，请勿刷新页面......";
        $('#OperateRestartresults').append('<p>连接中......</p>' );

        public.socketConn("/upgrade/execute", [])

        window.s.onopen = function (e) {
            window.s.send(JSON.stringify(postData));
        };
        
        window.s.onerror = function (){
            modal_head.innerHTML = "与服务器连接失败...";
            $('#OperateRestartresults').append('<p>连接失败......</p>' );
            setTimeout(function(){$('#runprogress').modal('hide');}, 1000);
        };

        window.s.onclose = function () {
            setTimeout(function(){$('#runprogress').modal('hide');}, 1000);
        };

        window.s.onmessage = function (e) {
            if (e.data == 'userNone'){
                toastr.error('未获取用户名，请重新登陆！', '错误');
                public.disableButtons(window.buttons, false);
                window.s.close();
                return false;
            }

            //return false;
            data = eval('('+ e.data +')')
            //console.log('message: ' + data['target']);//打印服务端返回的数据
            if (data.step == 'one'){
                $("#progress_bar").css("width", "50%");
                $('#OperateRestartresults').append('<p>连接成功......</p>' );
                modal_head.innerHTML = "升级执行中...";
            }else if (data.step == 'final'){
                modal_head.innerHTML = "升级执行完成...";
                $("#progress_bar").css("width", "100%");
                //$('#OperateRestartresults').append('<pre>' + data['result'] + '</pre>');
                $('#OperateRestartresults').append('<p>执行完成......</p>' );
                //console.log('websocket已关闭');
                setTimeout(function(){$('#runprogress').modal('hide');}, 1000);
                var html = "";
                var button = ""
                var button_html = "";
                for (var tgt in data.results){
                    //alert(tgt+data[tgt])
                    if (data['results'][tgt] == 'not return'){
                        button = [                        
                        '<div class="btn-group" style="width:18%; margin-bottom:5px;">',
                            '<button data-toggle="modal" data-target="#'+tgt+'" id="#'+tgt+'" type="button" class="btn btn-danger" style="width:100%;">'+tgt+'',
                            '</button>',
                        '</div>',].join("");
                    }else {
                        button = [                        
                        '<div class="btn-group" style="width:18%; margin-bottom:5px;">',
                            '<button data-toggle="modal" data-target="#'+tgt+'" id="#'+tgt+'" type="button" class="btn btn-info" style="width:100%;">'+tgt+'',
                            '</button>',
                        '</div>',].join("");
                    }

                    button_html = button_html + button + [
                        '<div class="modal fade" id="'+tgt+'" tabindex="-1" role="dialog" dialaria-labelledby="'+tgt+'" aria-hidden="true">',
                            '<div class="modal-dialog" style="width:1000px;">',
                                '<div class="modal-content" >',
                                    '<div class="modal-body">',
                                        '<xmp>'+data['results'][tgt]+'</xmp>',
                                    '</div>',
                                '</div>',
                            '</div>',
                        '</div>',].join("");
                    //$("#" + tgt).modal({keyboard: true});
                    //button = button + "<button class='btn btn-primary' data-toggle='modal' data-target='#show_results'>"+tgt+"</button>"
                    html = html + "<p><strong>"+tgt+"</strong></p><pre class='pre-scrollable'><xmp>"+data['results'][tgt]+"</xmp></pre>";
                }
                button_html = "<div class='btn-toolbar' role='toolbar'>" + button_html +"</div>" + "<hr>"
                $("#commandresults").html(button_html + html);
                for (var tgt in data.results){
                    $("#"+tgt).click(function(){
                        $(this).modal({keyboard: true});
                    });
                }
                window.s.close();
                return false;
            }
        }; 
        return false;
    },

};