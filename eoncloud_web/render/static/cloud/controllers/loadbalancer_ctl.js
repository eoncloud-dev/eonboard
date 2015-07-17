'use strict';
//负载资源controller
CloudApp.controller('LoadBalancerController', function ($rootScope, $scope, $filter, $interval, $modal, $i18next,status_desc, $timeout, ngTableParams, CommonHttpService, ToastrService) {
    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;
    $scope.status_desc = status_desc;
    //监控资源切换
    $scope.pools_tab = true;
    $scope.monitor_tab = false;
    $scope.tab_select = function(tab){
        if(tab == 'pools'){
            $scope.pools_tab = true;
            $scope.monitor_tab = false;
            $scope.loadbalancer_table.reload();
        }
        if(tab == 'monitor'){
            $scope.monitor_tab = true;
            $scope.pools_tab  = false;
            $scope.monitor_table.reload();
        }
    }
    //=======================================负载资源
    $scope.current_loadbalancer_data = [];
    $scope.loadbalancer_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get('/api/lbs/').then(function(data){
                var data_list = $filter('orderBy')(data, params.orderBy());

                params.total(data_list.length);

                $scope.current_loadbalancer_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());

                $defer.resolve($scope.current_loadbalancer_data);
            });
        }
    });
    //定时处理监控状态
   var timer = $interval(function () {
        var list = $scope.current_loadbalancer_data;
        var need_refresh = false;
        for (var i = 0; i < list.length; i++) {
            if (status_desc[list[i].status][1] == 0) {
                need_refresh = true;
                break;
            }
        }
        if (need_refresh) {
            $scope.loadbalancer_table.reload();
        }

    }, 5000);
    $rootScope.timer_list.push(timer);
    //=======================================start checkbox====================
    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_loadbalancer_data, function (item) {
            if($scope.status_desc[item.status][1]==1){
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            }
        });
    });

    // watch for data checkboxes
    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.current_loadbalancer_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_loadbalancer_data.length;

        angular.forEach($scope.current_loadbalancer_data, function (item) {
            if($scope.status_desc[item.status][1]==0){
                $scope.checkboxes.items[item.id] = false;
            }
            checked += ($scope.checkboxes.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes.checked = ((checked == total) && total != 0);
        }

        $scope.checked_count = checked;
        // grayed checkbox
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);
    //==================================end checkbox======================

    /*创建负载资源弹出窗口*/
    $scope.modal_create_loadbalancer = function () {
        $scope.balancer = {}
        var modalBalancer = $modal.open({
            templateUrl: 'create_balancer.html',
            controller: 'LoadBalancerCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                loadbalancer_table: function () {
                    return $scope.loadbalancer_table;
                },
                subnets:function(){
                    return CommonHttpService.get("/api/networks/subnets/")
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    /*修改负载资源弹出窗口*/
    $scope.modal_edit_loadbalancer = function(balancer){
        $scope.balancer = angular.copy(balancer);
        var modalBalancer = $modal.open({
            templateUrl: 'update_balancer.html',
            controller: 'LoadBalancerCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                loadbalancer_table: function () {
                    return $scope.loadbalancer_table;
                },
                subnets:function(){
                    return null;
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    //删除负载资源
    $scope.delete_balancer_action = function(){
        bootbox.confirm($i18next("balancer.confirm_delete_balancer"), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        var post_data = {
                            "pool_id":items_key[i]
                        }
                        CommonHttpService.post("/api/lbs/delete/", post_data).then(function (data) {
                            if (data.OPERATION_STATUS == 1) {
                                $scope.loadbalancer_table.reload();
                            }
                            else {
                                ToastrService.error(data.MSG, $i18next("op_failed"));
                            }
                        });
                        $scope.checkboxes.items[items_key[i]] = false;
                    }
                }
            }
        });
    }
    /*创建VIP弹出窗口*/
    $scope.modal_create_vip = function (balancer) {
        $scope.balancer = angular.copy(balancer);
        var modalBalancer = $modal.open({
            templateUrl: 'create_vip.html',
            controller: 'LoadBalancerCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                loadbalancer_table: function () {
                    return $scope.loadbalancer_table;
                },
                subnets:function(){
                    return null;
                },
                constant:function(){//获取创建相关常量信息
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    $scope.modal_edit_vip = function(balancer){
        $scope.balancer = angular.copy(balancer);
        $scope.vip = balancer.vip_info;
        $scope.vip.session_persistence = $scope.vip.session_persistence ==null?'-1':$scope.vip.session_persistence;
        var modalBalancer = $modal.open({
            templateUrl: 'update_vip.html',
            controller: 'LoadBalancerCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                loadbalancer_table: function () {
                    return $scope.loadbalancer_table;
                },
                subnets:function(){
                    return null;
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    //删除VIP
    $scope.delete_vip_action = function(balancer){
        bootbox.confirm($i18next("balancer.confirm_delete_vip"), function (confirm) {
            if (confirm) {
                var post_data = {
                    'pool_id':balancer.id
                }
                CommonHttpService.post("/api/lbs/vip/delete/", post_data).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        $scope.loadbalancer_table.reload();
                    }
                    else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                });
            }
        });
    }
    $scope.public_ip_action = function(balancer,action){
        $scope.balancer = angular.copy(balancer);
        $scope.action = action;
        var modalBalancer = $modal.open({
            templateUrl: 'attach_floatIp.html',
            controller: 'LoadBalancerFloatIpController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                loadbalancer_table: function () {
                    return $scope.loadbalancer_table;
                },
                floating_ips:function(){
                    var post_data = {
                        "action":action
                    }
                    return  CommonHttpService.get("/api/floatings/");
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }

    $scope.pool_monitor_assocation = function(balancer,action){
        $scope.balancer = angular.copy(balancer);
        $scope.action = action;
        var modalBalancer = $modal.open({
            templateUrl: 'attach_monitor.html',
            controller: 'LoadBalancerAttachMonitorsController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                loadbalancer_table: function () {
                    return $scope.loadbalancer_table;
                },
                monitors:function(){
                    var post_data = {
                        "action":action
                    }
                    return CommonHttpService.post("/api/lbs/getavmonitor/"+balancer.id+"/",post_data)
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    //=====================================end pool=============

    //===============================start monitor====================
    $scope.current_monitor_data = [];
    $scope.monitor_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get('/api/lbs/monitors/').then(function(data){
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : volume.name;
                params.total(data_list.length);
                $scope.current_monitor_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_monitor_data);
            });
        }
    });
    //===================================start monitor checkbox=======================
    $scope.checkboxes_monitor = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes_monitor.checked', function (value) {
        angular.forEach($scope.current_monitor_data, function (item) {
            if (angular.isDefined(item.id)) {
                $scope.checkboxes_monitor.items[item.id] = value;
            }
        });
    });

    // watch for data checkboxes
    $scope.$watch('checkboxes_monitor.items', function (values) {
        $scope.checked_monitor_count = 0;
        if (!$scope.current_monitor_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_monitor_data.length;

        angular.forEach($scope.current_monitor_data, function (item) {
            checked += ($scope.checkboxes_monitor.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes_monitor.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes_monitor.checked = ((checked == total) && total != 0);
        }

        $scope.checked_monitor_count = checked;
        // grayed checkbox
        angular.element(document.getElementById("select_all_monitor")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);
    //=======================end monitor checkbox=================
    /*创建监控弹出窗口*/
    $scope.modal_create_monitor = function () {
        $scope.monitor = null;
        var modalBalancer = $modal.open({
            templateUrl: 'create_monitor.html',
            controller: 'MonitorCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                monitor_table: function () {
                    return $scope.monitor_table;
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    $scope.modal_edit_monitor = function (monitor) {
        $scope.monitor = angular.copy(monitor);
        var modalBalancer = $modal.open({
            templateUrl: 'update_monitor.html',
            controller: 'MonitorCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                monitor_table: function () {
                    return $scope.monitor_table;
                },
                constant:function(){
                    return null;
                }
            }
        });
        modalBalancer.result.then(function (result) {
        }, function (result) {
        });
    }
    //删除监听器
    $scope.delete_monitor_action = function(){
        bootbox.confirm($i18next("balancer.confirm_delete_monitor"), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes_monitor.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        var post_data = {
                            "monitor_id":items_key[i]
                        }
                        CommonHttpService.post("/api/lbs/monitors/delete/", post_data).then(function (data) {
                            if (data.OPERATION_STATUS == 1) {
                                $scope.monitor_table.reload();
                            }
                            else {
                                ToastrService.error(data.MSG, $i18next("op_failed"));
                            }
                        });
                        $scope.checkboxes_monitor.items[items_key[i]] = false;
                    }
                }
            }
        });
    }
    //========================================end monitor===============

});

//负载资源创建controller
CloudApp.controller('LoadBalancerCreateController', function ($rootScope, $scope, $modalInstance, $i18next, $timeout,CommonHttpService, ToastrService,ValidationTool, constant,subnets,loadbalancer_table) {
    $scope.cancel = function () {
        $modalInstance.dismiss();
    };
    //获取创建相关常量信息，协议/会话类型/负载方法/监控类型
    $scope.constant = constant;
    $scope.subnets = subnets;

    $scope.flag = true;
    //create balancer confirm submit
    $scope.submit_balancer_click = function (balancer){
        if(!$scope.flag){
            return $scope.flag;
        }
        $scope.flag = false;
        ValidationTool.init('#create_balancer_form', {});
        if(!$("#create_balancer_form").validate().form()){
            $scope.flag = true;
            return;
        }
        var post_data = {
            "name":balancer.name,
            "description":balancer.description,
            "lb_method":balancer.lb_method,
            "subnet":balancer.subnet,
            "protocol":balancer.protocol
        }
        if (balancer.id  && balancer.id !=''){
            post_data.pool_id = balancer.id;
            post_data.subnet = balancer.subnet;
            post_data.protocol = balancer.protocol;
        }else{
            post_data.subnet = balancer.subnet;
            post_data.protocol = balancer.protocol;
        }

        CommonHttpService.post("/api/lbs/create/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success(data.MSG, $i18next("success"));
                loadbalancer_table.reload();
            }
            else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }
            $modalInstance.dismiss();
        });
    }

    //create vip confirm submit
    $scope.submit_vip_click = function (vip){
        if(!$scope.flag){
            return $scope.flag;
        }
        $scope.flag = false;
        ValidationTool.init('#create_vip_form', {});
        if(!$("#create_vip_form").validate().form()){
            $scope.flag = true;
            return;
        }
        var post_data = {
            "name":vip.name,
            "pool":$scope.balancer.id,
            "subnet":$scope.balancer.subnet,
            "description":vip.description,
            "protocol_port":vip.protocol_port,
            "protocol":$scope.balancer.protocol,
            "connection_limit":vip.connection_limit
        }
        if(vip.session_persistence !=undefined  && vip.session_persistence>=0){
            post_data.session_persistence = vip.session_persistence;
        }

        if (vip.id && vip.id !=''){
            post_data.vip_id = vip.id;
            post_data.protocol = vip.protocol
        }
        CommonHttpService.post("/api/lbs/vip/create/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success(data.MSG, $i18next("success"));
                loadbalancer_table.reload();
            }
            else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }

        });
        $modalInstance.dismiss();
    }

});

//关联监听器controller
CloudApp.controller('LoadBalancerAttachMonitorsController', function ($rootScope, $scope, $modalInstance, $i18next,CommonHttpService, ToastrService, monitors,loadbalancer_table) {
    $scope.cancel = function () {
        $modalInstance.dismiss();
    };
    $scope.has_error = false;
    $scope.monitors = monitors;
    //create vip confirm submit
    $scope.submit_attach_monitor_click = function (monitor){

        if (monitor == undefined || monitor == ''){
            $scope.has_error = true;
            return ;
        }
        var post_data = {
            "pool_id":$scope.balancer.id,
            "monitor_id":monitor,
            "action":$scope.action
        }

        CommonHttpService.post("/api/lbs/poolmonitoraction/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success(data.MSG, $i18next("success"));
                loadbalancer_table.reload();
            }
            else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }

        });
        $modalInstance.dismiss();
    }

});
//绑定公网ipcontroller
CloudApp.controller('LoadBalancerFloatIpController', function ($rootScope, $scope,$state, $modalInstance, $i18next,CommonHttpService, ToastrService, floating_ips,loadbalancer_table) {
    $scope.cancel = function () {
        $modalInstance.dismiss();
    };

    $scope.floating_ips = [];
    if(floating_ips.length>0){
        if($scope.action == 'associate'){
            for (var i = 0; i < floating_ips.length; i++) {
                if (floating_ips[i].status == 10 && floating_ips[i].resource == null) {
                    $scope.floating_ips.push(floating_ips[i]);
                }
            }
        }else{
            for (var i = 0; i < floating_ips.length; i++) {
                if (floating_ips[i].status == 20 && floating_ips[i].resource_info.id == $scope.balancer.id) {
                    $scope.floating_ips.push(floating_ips[i]);
                }
            }
        }


    }
    $scope.has_error = false;
    //float ip operation
    $scope.submit_attach_floatIp_click = function (floatIp){
        if(floatIp == undefined || floatIp == ''){
            $scope.has_error = true;
            return false;
        }
        var post_data = {
            "floating_id":floatIp,
            "action":$scope.action,
            "resource": $scope.balancer.id,
            "resource_type":"LOADBALANCER"
        }

        CommonHttpService.post("/api/floatings/action/", post_data).then(function (data) {
            $modalInstance.dismiss();
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success($i18next("floatingIP.op_success_and_waiting"), $i18next("success"));
                $state.go("floating");
                Layout.setSidebarMenuActiveLink('match');
            }
            else {
                ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
            }
        });
    }

});


//监控创建controller
CloudApp.controller('MonitorCreateController', function ($rootScope, $scope, $modalInstance, $i18next, $timeout,CommonHttpService, ToastrService,ValidationTool, constant,monitor_table) {
    $scope.cancel = function () {
        $modalInstance.dismiss();
    };

    $scope.constant = constant;

    $scope.timeout_error =false;


    $scope.$watch('timeout', function (value) {
        $scope.timeout_error =false;

    });


    //控制表单重复提交
    $scope.flag = true;
    //create balancer confirm submit
    $scope.submit_click = function (monitor){
        if(!$scope.flag){
            return $scope.flag;
        }
        $scope.flag = false;

        ValidationTool.init('#create_monitor_form', {});
        if(!$("#create_monitor_form").validate().form()){
            $scope.flag = true;
            return;
        }

        var delay  =$scope.monitor.delay;
        var timeout  =$scope.monitor.timeout;
        if(delay && timeout){
            if(timeout > delay){
                $scope.timeout_error = true;
            }
        }
        console.log(12121)
        if($scope.timeout_error){
            $scope.flag = true;
            return
        }
        var post_data = {
            "name":monitor.name,
            "delay":monitor.delay,
            "timeout":monitor.timeout,
            "max_retries":monitor.max_retries,
            "type":monitor.type
        }
        if(monitor.id && monitor.id!=''){
            post_data.monitor_id = monitor.id;
            post_data.type = monitor.type
        }else{
            post_data.type=monitor.type;
            if(monitor.monitor_type == '2' || monitor.monitor_type == '3'){
                post_data.url_path = monitor.url_path;
                post_data.expected_codes = monitor.expected_codes;
            }
        }
        CommonHttpService.post("/api/lbs/monitors/create/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success(data.MSG, $i18next("success"));
                monitor_table.reload();
            }
            else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }
        });

        $modalInstance.dismiss();
    }
});


//负载均衡详情页controller
CloudApp.controller('LoadBalancerInfoController', function ($rootScope, $scope, $filter, $interval, $modal, $i18next, $timeout, status_desc,ngTableParams,CommonHttpService, ToastrService, balancer_id) {
    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });
    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;
    $scope.status_desc = status_desc;
    CommonHttpService.get("/api/lbs/"+balancer_id+"/").then(function(data){
        $scope.balancer = data;
    });


    $scope.current_member_data = [];
    $scope.member_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get('/api/lbs/members/'+balancer_id+'/').then(function(data){
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : volume.name;
                params.total(data_list.length);
                $scope.current_member_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_member_data);
            });
        }
    });
    //定时处理监控状态
    var timer = $interval(function () {
        var list = $scope.current_member_data;
        var need_refresh = false;
        for (var i = 0; i < list.length; i++) {
            if (status_desc[list[i].status][1] == 0) {
                need_refresh = true;
                break;
            }
        }
        if (need_refresh) {
            $scope.member_table.reload();
        }

    }, 5000);
    $rootScope.timer_list.push(timer);
    //=======================================start checkbox====================
    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_member_data, function (item) {
            if($scope.status_desc[item.status][1]==1){
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            }
        });
    });

    // watch for data checkboxes
    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.current_member_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_member_data.length;

        angular.forEach($scope.current_member_data, function (item) {
            if($scope.status_desc[item.status][1]==0){
                $scope.checkboxes.items[item.id] = false;
            }
            checked += ($scope.checkboxes.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes.checked = ((checked == total) && total != 0);
        }

        $scope.checked_count = checked;
        // grayed checkbox
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);

    $scope.add_member = function(balancer){
        var modalmember = $modal.open({
            templateUrl: 'add_member.html',
            controller: 'LoadBalancerMemberController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                member_table: function () {
                    return $scope.member_table;
                },
                instances:function(){
                    console.log($scope.member_table)
                    var members = $scope.member_table.data;
                    var av_instance = [];
                    var instances = CommonHttpService.get("/api/instances/search/").then(function(data){
                        if(data.length >0 ){
                            for(var i=0;i<data.length;i++){
                                var flag = true;
                                var instance = data[i];
                                if(members.length>0){
                                    for(var j=0;j<members.length;j++){
                                        var member = members[j];
                                        if(instance.id == member.instance){
                                            flag = false;
                                            break;
                                        }
                                    }
                                }
                                if(flag){
                                    av_instance.push(instance)
                                }
                            }
                        }
                    });
                    return av_instance;
                }
            }
        });
        modalmember.result.then(function (result) {
        }, function (result) {
        });
    }
    //编辑成员
    $scope.modal_edit_member = function(member){
        $scope.member = angular.copy(member);
        var modalmember = $modal.open({
            templateUrl: 'update_member.html',
            controller: 'LoadBalancerMemberController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                member_table: function () {
                    return $scope.member_table;
                },
                instances:function(){
                    return null;
                }
            }
        });
        modalmember.result.then(function (result) {
        }, function (result) {
        });
    }

    //删除成员
    $scope.delete_member_action = function(){
        bootbox.confirm($i18next("balancer.confirm_delete_member"), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        var post_data = {
                            "member_id":items_key[i]
                        }
                        CommonHttpService.post("/api/lbs/members/delete/", post_data).then(function (data) {
                            if (data.OPERATION_STATUS == 1) {
                                $scope.member_table.reload();
                            }
                            else {
                                ToastrService.error(data.MSG, $i18next("op_failed"));
                            }
                        });
                        $scope.checkboxes.items[items_key[i]] = false;
                    }
                }
            }
        });
    }
});


//负载均衡member添加controller
CloudApp.controller('LoadBalancerMemberController', function ($rootScope, $scope, $filter, $i18next,$modalInstance,CommonHttpService, ToastrService,ValidationTool,member_table,instances) {
    $scope.cancel = function () {
        $modalInstance.dismiss();
    };

    //控制表单重复提交
    $scope.flag = true;


    $scope.instances = instances;
    $scope.submit_member_click = function(member){
        if(!$scope.flag){
            return $scope.flag;
        }
        $scope.flag = false;
        ValidationTool.init('#create_member_form', {});
        if(!$("#create_member_form").validate().form()){
            $scope.flag = true;
            return;
        }
        var post_data = {
            "pool":$scope.balancer.id,
            "weight":member.weight,
            "protocol_port":member.protocol_port
        }
        if(member.id && member.id!=''){
            post_data.member_id  = member.id;
        }else{
            var members = ""
            if(member.members.length>0){
                for(var i=0;i< member.members.length ;i++){
                    if(members !=''){
                        members +=','
                    }
                    members += member.members[i].id
                }
            }
            post_data.members  = members;
        }
        CommonHttpService.post("/api/lbs/members/create/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success(data.MSG, $i18next("success"));
                member_table.reload();
            }
            else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }
        });
        $modalInstance.dismiss();
    }
});
