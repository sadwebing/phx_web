$(function () {
    tableInit.Init();
    operate.operateInit();
});

window.product_list_html = {}

//初始化表格
var tableInit = {
    Init: function () {
        //this.dbclick();
        //绑定table的viewmodel
        this.myViewModel = new ko.bootstrapTableViewModel({
            //url: '/monitor/project/Query',         //请求后台的URL（*）
            //method: 'post',                      //请求方式（*）
            dataType: "json",
            toolbar: '#toolbar',                //工具按钮用哪个容器
            clickToSelect: true,
            toolbarAlign: "right",
            queryParams: function (param) {
                return { limit: param.limit, offset: param.offset, 'act':'query_all' };
            },//传递参数（*）
            columns: [
                {
                    checkbox: true,
                    width:'2%',
                },{
                    field: 'id',
                    title: 'id',
                    sortable: true,
                    formatter: function (value, row, index) {
                        row.id = index+1;
                        return index+1;
                    }
                    //width:'8%',
                    //align: 'center'
                },{
                    field: 'product',
                    title: 'product',
                    sortable: true,
                    //width:'8%',
                    //align: 'center'
                },{
                    field: 'zone',
                    title: 'zone',
                    sortable: true,
                    //width:'15%',
                    //align: 'center'
                },{
                    field: 'name',
                    title: 'name',
                    sortable: true,
                    //width:'15%',
                    //align: 'center'
                },{
                    field: 'type',
                    title: 'type',
                    sortable: true,
                    //width:'5%',
                    //align: 'center'
                },{
                    field: 'value',
                    title: 'content',
                    sortable: true,
                    //width:'15%',
                    //align: 'center'
                },{
                    field: 'record_line',
                    title: '线路',
                    sortable: true,
                    //width:'15%',
                    //align: 'center'
                },{
                    field: 'record_id',
                    title: 'record_id',
                    sortable: true,
                    //width:'auto',
                    //align: 'center'
                },{
                    field: 'enabled',
                    title: '状态',
                    sortable: true,
                    //width:'5%',
                    events: operateStatusEvents,
                    formatter: this.operateStatusFormatter,
                    //align: 'center'
                },{
                    field: 'zone_id',
                    title: 'zone_id',
                    sortable: true,
                    //width:'auto',
                    //align: 'center'
                },{
                    field: 'operations',
                    title: '操作项',
                    //align: 'center',
                    width:'6%',
                    checkbox: false,
                    //events: operateEvents,
                    events: operateStatusEvents,
                    formatter: this.operateFormatter,
                    //width:300,
                },
            ]

        });
        //this.myViewModel.hidecolumn('zone_id');
        //this.myViewModel.hidecolumn('record_id');
        ko.applyBindings(this.myViewModel, document.getElementById("records_table"));
    },

    dbclick: function (){
        $('#records_table').on('all.bs.table', function (e, name, args) {
            //console.log('Event:', name, ', data:', args);
        }).on('dbl-click-cell.bs.table', function (e, field, value, row, $element) {
            console.log(row)
            //return false;
            $("#myModal").modal().on("shown.bs.modal", function () {
                //将选中该行数据有数据Model通过Mapping组件转换为viewmodel
                ko.utils.extend(operate.DepartmentModel, ko.mapping.fromJS(row));
                if (document.getElementById(operate.DepartmentModel.id()).checked){
                    operate.DepartmentModel.status_ = 'active';
                }else {
                    operate.DepartmentModel.status_ = 'inactive';
                }
                ko.applyBindings(operate.DepartmentModel, document.getElementById("myModal"));
                operate.operateSave('Update');
            }).on('hidden.bs.modal', function () {
                //关闭弹出框的时候清除绑定(这个清空包括清空绑定和清空注册事件)
                ko.cleanNode(document.getElementById("myModal"));
            });

        });
    },

    operateStatusFormatter: function (value,row,index){
        if (row.enabled == '1'){
            content = [
            '<div class="checkbox checkbox-slider--a" style="margin:0px;">',
                '<label>',
                    '<input type="checkbox" id='+ row.record_id +' class="update_status" checked><span></span>',
                '</label>',
            '</div>'
            ].join('');
        }else if (row.enabled == '0'){
            content = [
            '<div class="checkbox checkbox-slider--a" style="margin:0px;">',
                '<label>',
                    '<input type="checkbox" id='+ row.record_id +' class="update_status"><span></span>',
                '</label>',
            '</div>'
            ].join('');
        }else {
            content = ['<p>unknown</p>']
        }
        return content;
    },

    operateFormatter: function (value,row,index){
        content = [
        '<a class="delete_record" href="javascript:void(0)" title="删除记录">',
        '<i class="text-primary"> 删除</i>',
        '</a>'
        ].join('');
        return content;
    },
};

window.operateStatusEvents = {
    'click .update_status': function (e, value, row, index) {
        var postData = [row];
        if (document.getElementById(row.record_id).checked){
            postData[0].enabled = '1';
            //console.log(postData);
        }else {
            postData[0].enabled = '0';
            //console.log(postData);
        }
        $.ajax({
            url: "/dns/dnspod/update_records",
            type: "post",
            data: JSON.stringify(postData),
            success: function (data, enabled) {
                if (postData[0].enabled == '1'){
                    toastr.success(row.product+": "+row.name, '域名解析已启用');
                }else {
                    toastr.warning(row.product+": "+row.name, '域名解析已禁用');
                }
                
                //ko.cleanNode(document.getElementById("tomcat_table"));
                row.enabled = postData[0].enabled;
                //alert(data);
                //tableInit.myViewModel.refresh();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                if (postData[0].enabled == '1'){
                    document.getElementById(row.record_id).checked = false;
                }else {
                    document.getElementById(row.record_id).checked = true;
                }
                if (XMLHttpRequest.enabled == '0'){
                    toastr.error('后端服务不响应', '错误')
                }else {
                    toastr.error(XMLHttpRequest.responseText, XMLHttpRequest.enabled)
                }
                //console.info(XMLHttpRequest)
                //alert(XMLHttpRequest.enabled+': '+XMLHttpRequest.responseText);
                //tableInit.myViewModel.refresh();
            }
        });
        return false;
    },

    'click .delete_record': function (e, value, row, index) {
        var postData = [row];
        var row_d    = {'index': row.id-1};
        //console.log(row);

        //删除前先隐藏删除列
        tableInit.myViewModel.hideRow(row_d);
        //setTimeout(function(){tableInit.myViewModel.showRow(row_d)}, 2000);
        //tableInit.myViewModel.showRow(row_d);

        $.ajax({
            url: "/dns/dnspod/delete_records",
            type: "post",
            data: JSON.stringify(postData),
            success: function (data, enabled) {
                toastr.success(row.product+": "+row.name, '域名删除成功');
                //删除列表行
                tableInit.myViewModel.remove({
                    'field': 'id',
                    'values': [row.id]
                });
                
                //alert(data);
                //tableInit.myViewModel.refresh();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                //删除失败，重新展示行
                tableInit.myViewModel.showRow(row_d);
                
                if (XMLHttpRequest.enabled == '0'){
                    toastr.error('后端服务不响应', '错误')
                }else {
                    toastr.error(XMLHttpRequest.responseText, XMLHttpRequest.enabled)
                }
                //console.info(XMLHttpRequest)
                //alert(XMLHttpRequest.enabled+': '+XMLHttpRequest.responseText);
                //tableInit.myViewModel.refresh();
            }
        });
        return false;
    },
};

//操作
var operate = {
    //初始化按钮事件
    operateInit: function () {
        tableInit.myViewModel.hidecolumn('zone_id');
        tableInit.myViewModel.hidecolumn('record_id');
        //this.operateCheckStatus();
        this.isIp();
        this.GetDnsPodProduct();
        this.selectpicker();
        this.operateSearch();
        this.operateEdit();
        this.detectDns();
        //this.operateCommitEdit();
        this.DepartmentModel = {
            id: ko.observable(),
            envir: ko.observable(),
            project: ko.observable(),
            minion_id: ko.observable(),
            ip_addr: ko.observable(),
            server_type: ko.observable(),
            role: ko.observable(),
            domain: ko.observable(),
            url: ko.observable(),
            status_: ko.observable(),
            info: ko.observable(),
        };
    },

    selectpicker: function docombjs() {
        $('.selectpicker').selectpicker({
            style: 'btn-default',
            //width: "auto",
            size: 15,
            showSubtext:true,
        });
    },

    detectDns: function () {
        $('#detect_dns').on("click", function () {
            
        });
    },

    isIp: function (value) {
        var regexp = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
                 
        var valid = regexp.test(value);
        if(!valid){//首先必须是 xxx.xxx.xxx.xxx 类型的数字，如果不是，返回false
            return false;
        }
             
        return value.split('.').every(function(num){
            //切割开来，每个都做对比，可以为0，可以小于等于255，但是不可以0开头的俩位数
            //只要有一个不符合就返回false
            if(num.length > 1 && num.charAt(0) === '0'){
                //大于1位的，开头都不可以是‘0’
                return false;
            }else if(parseInt(num , 10) > 255){
                //大于255的不能通过
                return false;
            }
            return true;
        });
    },

    isDomain: function (value, proxied) {
        var regexp = /^.*[a-zA-Z0-9]+.*\.[a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$/;
        var regexp_tw = /^(tw|.*\.tw)\..*$/;

        var valid = regexp.test(value);
        if(!valid){
            return false;
        }

        if (proxied == 'false'){
            var valid_tw = regexp_tw.test(value);

            if(valid_tw){
                return false;
            }
        }


        return true;
    },

    GetDnsPodProduct: function(){
        operate.disableButtons(['btn_repost', 'btn_op_search'], true);
        toastr.info("正在获取数据，请耐心等待返回...");

        $.ajax({
            url: "/dns/dnspod/get_product_records",
            type: "post",
            contentType: 'application/json',
            //data: JSON.stringify(postData),
            success: function (datas, status) {
                operate.disableButtons(['btn_repost', 'btn_op_search'], false);
                toastr.success('数据获取成功！');
                //alert(datas);
                var data = eval('('+datas+')');
                var product_html = "";

                $.each(data, function (index, item) { 
                    var domain_html = "";
                    product_html = product_html + "<option value="+item.product+">"+item.product+"</option>";
                    //循环获取数据 
                    $.each(item.domain, function (index, domain) {
                        if (domain.status == 'enable'){
                            domain_html = domain_html + "<option value='"+domain.id+"_"+item.product+"' data-subtext='"+item.product+"'>"+domain.name+"</option>";
                        }
                    })

                    product_list_html[item.product] = domain_html;
                })
                document.getElementById('dp_product').innerHTML=product_html;
                //$('.selectpicker').selectpicker({title:"请选择服务器地址"});
                $('.selectpicker').selectpicker('refresh');
            },
            error:function(msg){
                alert("获取项目失败！");
                return false;
            }
        });
    },
    
    setProductHtml: function(value){
        var productlist = []
        //var project = document.getElementById("project_active").value;
        objSelectproject = document.productform.dp_product;
        
        for(var i = 0; i < objSelectproject.options.length; i++) { 
            if (objSelectproject.options[i].selected == true) 
            productlist.push(objSelectproject.options[i].value);
        }
        var html = "";

        for (var num in productlist){
            product = productlist[num];
            html = html + product_list_html[product];
        }
        document.getElementById(value).innerHTML=html;
        //$('.selectpicker').selectpicker({title:"请选择服务器地址"});
        $('.selectpicker').selectpicker('refresh');
        return false;
    },
    
    //查询zone记录
    operateSearch: function () {
        $('#btn_op_search').on("click", function () {
            var zone_list = []

            var objSelectzone = document.domainsform.zone_name; 
            for(var i = 0; i < objSelectzone.options.length; i++) { 
                if (objSelectzone.options[i].selected == true){
                    var tmp = {}
                    tmp['id'] = objSelectzone.options[i].value.split('_')[0];
                    tmp['name'] = objSelectzone.options[i].text;
                    tmp['product'] = objSelectzone.options[i].value.split('_')[1];
                    zone_list.push(tmp);
                }
            }
            //console.log(zone_list);
            var params = {
                url: '/dns/dnspod/get_zone_records',
                method: 'post',
                singleSelect: false,
                queryParams: function (param) {
                    return { limit: param.limit, offset: param.offset, 'postdata':zone_list };
                },
            }
            tableInit.myViewModel.refresh(params);

        });
    },

    ViewModel: function() {
                var self = this;
                self.datas = ko.observableArray();
    },

    //修改zone记录
    operateEdit: function () {
        $('#btn_edit').on("click", function () {
            $("#progress_bar_update_record").css("width", "0%");
            document.getElementById('update_record_finished_count').innerHTML="finished: 0  &emsp;  success: 0  &emsp;  failed: 0";
            document.getElementById('record_content').value = "";
            operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
            var arrselectedData = tableInit.myViewModel.getSelections();
            if (arrselectedData.length <= 0){
                alert("请至少选择一行数据");
                return false;
            }

            var options = document.getElementById('record_type').children;
            options[0].selected=true;

            var options = document.getElementById('record_status').children;
            options[0].selected=true;

            var vm = new operate.ViewModel();
            for (var i=0;i<arrselectedData.length;i++){
                //ko.utils.extend(operate.DepartmentModel, ko.mapping.fromJS(arrselectedData[i]));
                //vm.datas.push(operate.DepartmentModel);
                vm.datas.push(ko.mapping.fromJS(arrselectedData[i]));
            }
            $("#confirmEditModal").modal().on("shown.bs.modal", function () {
                //ko.utils.extend(operate.DepartmentModel, ko.mapping.fromJS(arrselectedData));
                //ko.applyBindings(operate.DepartmentModel, document.getElementById("confirmEditModal"));
                ko.applyBindings(vm, document.getElementById("confirmEditModal"));
                //datas = ko.mapping.fromJS(arrselectedData)
                var html = "";
                $.each(vm.datas(), function (index, item) { 
                    //循环获取数据
                    var record = vm.datas()[index];
                    //console.log(record);
                    //alert(record)
                    html_record = "<tr id="+record.name()+"><td>"+record.product()+"</td><td>"+record.zone()+"</td><td>"+record.name()+"</td><td>"+record.type()+"</td><td>"+record.value()+"</td><td>"+record.enabled()+"</td></tr>";
                    html = html + html_record
                }); 
                $("#EditDatas").html(html);
                operate.operateCommitEdit();
                //vm.datas.valueHasMutated();
            }).on('hidden.bs.modal', function () {
                //关闭弹出框的时候清除绑定(这个清空包括清空绑定和清空注册事件)
                ko.cleanNode(document.getElementById("confirmEditModal"));
            });
        });
    },

    operateCommitEdit: function () {
        $('#btn_commit_edit').on("click", function () {
            $("#progress_bar_update_record").css("width", "0%");
            document.getElementById('update_record_finished_count').innerHTML="finished: 0  &emsp;  success: 0  &emsp;  failed: 0";
            operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], true);
            var arrselectedData = tableInit.myViewModel.getSelections();
            var postdata = {};
            postdata['type'] = $("#record_type option:selected").val()
            if (! postdata['type']){
                alert('pls select the type!');
                operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                return false;
            }
            postdata['enabled'] = $("#record_status option:selected").val()
            if (! postdata['enabled']){
                alert('pls select the status!');
                operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                return false;
            }
            postdata['value'] = document.getElementById('record_content').value.replace(/(^\s*)|(\s*$)/g, "");
            if (! postdata['value']){
                alert('content can\'t be empty!');
                operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                return false;
            }

            if (postdata['type'] == 'A') {
                if (! operate.isIp(postdata['value'])){
                    alert('Content for A record is invalid.');
                    operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                    return false;
                }
            }else if (postdata['type'] == 'CNAME'){
                if (! operate.isDomain(postdata['value'], postdata['enabled'])){
                    alert('Content for CNAME record is invalid.');
                    operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                    return false;
                }
            }

            postdata['records'] = arrselectedData;
            count = postdata['records'].length;
            success = 0;
            failed = 0;

            var socket = new WebSocket("ws://" + window.location.host + "/dns/dnspod/update_records");
            socket.onopen = function () {
                //console.log('WebSocket open');//成功连接上Websocket
                socket.send(JSON.stringify(postdata));
            };
            //$('#runprogress').modal('show');
            socket.onerror = function (){
                toastr.error('后端服务不响应', '错误');
                operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
            };
            socket.onclose = function () {
                //setTimeout(function(){$('#confirmEditModal').modal('hide');}, 1000);
                toastr.info('连接已关闭...');
                operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
            };
            socket.onmessage = function (e) {

                console.log(e.data);

                if (e.data == 'userNone'){
                    toastr.error('未获取用户名，请重新登陆！', '错误');
                    operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                    socket.close();
                    return false;
                }

                data = eval('('+ e.data +')');
                var width = 100*(data.step)/count + "%";
                if (data.result){
                    success = success + 1;
                    document.getElementById(data.record.name).style.backgroundColor = "white";
                }else {
                    failed = failed + 1;
                    document.getElementById(data.record.name).style.backgroundColor = "red";
                }
                document.getElementById('update_record_finished_count').innerHTML="finished: "+data.step+"  &emsp;  success: "+success+"  &emsp;  failed: "+failed+"";
                $("#progress_bar_update_record").css("width", width);
                if (data.step == count){
                    socket.close();
                    operate.disableButtons(['btn_close_edit', 'btn_commit_edit'], false);
                }
            };
            return false;
        });
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

    //数据校验
    operateCheck:function(arr){
        if (arr.length <= 0) {
            alert("请至少选择一行数据");
            return false;
        }
        if (arr.length > 1) {
            alert("只能编辑一行数据");
            return false;
        }
        return true;
    }
}