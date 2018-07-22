$(function () {
    servers.operateInit();
});

window.servers_list = {'item': []}

//操作
var servers = {
    //初始化按钮事件
    operateInit: function () {
        //this.GetServersRecords();
        this.getItemsValue();
    },

    disableButtons: function (buttonList, fun) {
        for (var i = 0; i < buttonList.length; i++){
            if (fun){
                document.getElementById(buttonList[i]).disabled = true;
            }else {
                document.getElementById(buttonList[i]).disabled = false;
            }
        }
    },

    getItemsValue: function (){
        var objSelect = document.getElementById("item_privkey_select"); 
        for(var i = 0; i < objSelect.options.length; i++) { 
            if (objSelect.options[i].value == ""){
                continue;
            }
            servers_list['item'].push(objSelect.options[i].value);
        }
        //console.log(servers_list);
    },

    isNumber: function(value){
        var regPos = /^\d+(\.\d+)?$/; //非负浮点数
        var regNeg = /^(-(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*)))$/; //负浮点数
        if(regPos.test(value) || regNeg.test(value)) {
            return true;
            } else {
            return false;
            }
    },


    getAllSelectValue: function (value){
        var selectedValue = []; 
        var objSelect = document.getElementById(value); 
        for(var i = 0; i < objSelect.options.length; i++) { 
            if (objSelect.options[i].value == ""){
                continue;
            }
            if (servers.isNumber(objSelect.options[i].value)){
                var t = parseInt(objSelect.options[i].value);
            }else {
                var t = objSelect.options[i].value;
            }
            selectedValue.push(t);
        }
        return selectedValue;
    },

    showSelectedValue: function (value){
        var selectedValue = []; 
        var objSelect = document.getElementById(value); 
        for(var i = 0; i < objSelect.options.length; i++) { 
            if (objSelect.options[i].selected == true) {
                if (typeof(objSelect.options[i].value) == "number"){
                    var t = parseInt(objSelect.options[i].value);
                }else {
                    var t = objSelect.options[i].value;
                }
                selectedValue.push(t);
            }
        }

        if (selectedValue.length == 0){
            return servers.getAllSelectValue(value);
        }

        return selectedValue;
    },

    DisplayPanel: function (select, value){
        selected = document.getElementById(select);
        //console.log(selected.value);
        for(var i = 0; i < servers_list['item'].length; i++) { 
            var item = servers_list['item'][i];
            //console.log(value+"_"+servers_list['item'][i])
            document.getElementById(value+"_"+servers_list['item'][i]).style.display = "none";
        }
        document.getElementById(value+"_"+selected.value).style.display = "inline";    
    },


    GetServersRecords: function(value){
        toastr.info("正在获取数据，请耐心等待返回...");
        var postData = {
            'privkey':{},
            'envir': servers.showSelectedValue('item_envir'),
            'product': servers.showSelectedValue('item_product'),
            'project': servers.showSelectedValue('item_project'),
            'server_type': servers.showSelectedValue('item_server_type'),
        }

        for(var i = 0; i < servers_list['item'].length; i++) { 
            var item = servers_list['item'][i];
            postData['privkey'][servers_list['item'][i]] = document.getElementById(value+"_"+servers_list['item'][i]).value;
        }

        $.ajax({
            url: "/servers/get_servers_records",
            type: "post",
            contentType: 'application/json',
            data: JSON.stringify(postData),
            success: function (datas, status) {
                //alert(datas);
                var data = eval(datas);
                initData = [];
                $.each(data, function (index, item) { 
                    //servers_list['item'].push([item.envir, item.product, item.project, item.server_type].join('_'))

                    $.each(item.minions, function (index, minion) { 
                        //console.log(data.minions['index']);
                        initData.push({
                            'envir':       item.envir,
                            'product':     item.product,
                            'project':     item.project,
                            'server_type': item.server_type,
                            'role':        item.role,
                            'uri':         item.uri,
                            'proj_info':   item.info,
                            'minion_id':   minion.minion_id,
                            'user':        minion.user,
                            'port':        minion.port,
                            'password':    minion.password,
                            'price':       minion.price,
                            'provider':    minion.provider,
                            'info':        minion.info,
                            'ip':          minion.ip,
                        })
                    });
                });
                //console.log(initData);
                tableInit.myViewModel.load(initData);
                toastr.success('数据获取成功！');
            },
            error:function(msg){
                alert("获取项目失败！");
                return false;
            }
        });
    },
    
    selectpicker: function docombjs() {
        $('.selectpicker').selectpicker({
            style: 'btn-default',
            //width: "auto",
            size: 15,
            showSubtext:true,
        });
    },
};