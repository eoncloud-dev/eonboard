 'use strict';

CloudApp.controller('FirewallController', function($rootScope, $scope, $filter, $i18next,$timeout,$modal,ngTableParams, Firewall,CommonHttpService,ToastrService) {
    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;
    $scope.current_firewall_data = []


    $scope.firewall_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],

        getData: function ($defer, params) {
            Firewall.query(function (data) {
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : name;
                params.total(data_list.length);
                $scope.current_firewall_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_firewall_data);
            });
        }
    });
    /////////////////////////
    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_firewall_data, function (item) {
            if (angular.isDefined(item.id)) {
                $scope.checkboxes.items[item.id] = value;
            }
        });
    });

    // watch for data checkboxes
    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.current_firewall_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_firewall_data.length;

        angular.forEach($scope.current_firewall_data, function (item) {
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

    // open create firewall page
    $scope.modal_create_firewall = function(){
        $modal.open({
            templateUrl: 'create_firewall.html',
            controller: 'FirewallCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                firewall_table: function () {
                    return $scope.firewall_table;
                }
            }
        });
    }



    $scope.batch_action = function (action) {
        bootbox.confirm($i18next("firewall.confirm_" + action), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        var post_data = {
                            "id":items_key[i]
                        }
                        CommonHttpService.post("/api/firewall/delete/", post_data).then(function (data) {
                            if (data.OPERATION_STATUS == 1) {
                                ToastrService.success(data.MSG, $i18next("success"));
                                $scope.firewall_table.reload();
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




 CloudApp.controller('FirewallCreateController',
     function($rootScope, $scope,$modalInstance,firewall_table,ToastrService,CommonHttpService,$i18next) {
         $scope.selected_rule = 'tcp';
         $scope.port_range = 'port';
         $scope.firewall = {}
         $scope.cancel = function () {
             $modalInstance.dismiss();
         };

         $scope.create = function(firewall){
             if($scope.firewall == undefined || $scope.firewall.name == null || $scope.firewall.name == "" ){
                 $scope.has_error = true ;
             }else{
                 var post_data = {
                     "name":firewall.name,
                     "desc":firewall.desc
                 }
                 CommonHttpService.post("/api/firewall/create/", post_data).then(function (data) {
                     if (data.OPERATION_STATUS == 1) {
                         ToastrService.success(data.MSG, $i18next("success"));
                         firewall_table.reload();
                     }
                     else {
                         ToastrService.error(data.MSG, $i18next("op_failed"));
                     }
                     $modalInstance.dismiss();
                 });
             }
         }
     });



 CloudApp.controller('FirewallRulesController', function($rootScope, $scope, $filter, $i18next,$timeout,$modal,ngTableParams,firewall_id,ToastrService,CommonHttpService) {
     $scope.$on('$viewContentLoaded', function() {
         Metronic.initAjax();
     });
     $scope.firewall_id = firewall_id;
     $rootScope.settings.layout.pageBodySolid = true;
     $rootScope.settings.layout.pageSidebarClosed = false;
     $scope.current_firewall_rules_data = []

     $scope.firewall_rules_table = new ngTableParams({
         page: 1,
         count: 10
     }, {
         counts: [],
         getData: function ($defer, params) {
             CommonHttpService.get("/api/firewall/firewall_rules/"+firewall_id+"/").then(function (data) {
                 var data_list = params.sorting() ?
                     $filter('orderBy')(data, params.orderBy()) : name;
                 params.total(data_list.length);
                 $scope.current_firewall_rules_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                 $defer.resolve($scope.current_firewall_rules_data);
             });
         }
     });
     /////////////////////////
     $scope.checkboxes = {'checked': false, items: {}};

     // watch for check all checkbox
     $scope.$watch('checkboxes.checked', function (value) {
         angular.forEach($scope.current_firewall_rules_data, function (item) {
             if (angular.isDefined(item.id)) {
                 $scope.checkboxes.items[item.id] = value;
             }
         });
     });

     // watch for data checkboxes
     $scope.$watch('checkboxes.items', function (values) {
         $scope.checked_count = 0;
         if (!$scope.current_firewall_rules_data) {
             return;
         }
         var checked = 0, unchecked = 0,
             total = $scope.current_firewall_rules_data.length;

         angular.forEach($scope.current_firewall_rules_data, function (item) {
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

     // open create firewall page
     $scope.modal_create_firewall_rule = function(){
         CommonHttpService.get("/api/firewall/default_rules/").then(function (data) {
             $scope.default_rules = data;
         });
         $modal.open({
             templateUrl: 'create_firewall_rule.html',
             controller: 'FirewallRuleCreateController',
             backdrop: "static",
             scope: $scope,
             resolve: {
                 firewall_rules_table: function () {
                     return $scope.firewall_rules_table;
                 }
             }
         });
     }

     $scope.delete_action = function (filrewall_rule) {
         bootbox.confirm($i18next("firewall.confirm_delete_rule"), function (confirm) {
             if (confirm) {
                var post_data ={
                    "id":filrewall_rule.id
                }
                 CommonHttpService.post("/api/firewall/firewall_rules/delete/", post_data).then(function (data) {
                     if (data.OPERATION_STATUS == 1) {
                         ToastrService.success(data.MSG, $i18next("success"));
                         $scope.firewall_rules_table.reload();
                     }
                     else {
                         ToastrService.error(data.MSG, $i18next("op_failed"));
                     }
                 });
             }
         });
     }
 });

 CloudApp.controller('FirewallRuleCreateController',
     function($rootScope, $scope,$modalInstance,firewall_rules_table,ToastrService,CommonHttpService,$i18next) {
         $scope.selected_rule = 'tcp';
         $scope.firewall_rule = {
             'port_range' : 'port'
         }
         $scope.firewall_rule_port = false;
         $scope.firewall_rule_form = false;
         $scope.firewall_rule_to = false;
         $scope.cancel = function () {
             $modalInstance.dismiss();
         };


         $scope.$watch('firewall_rule.port',function(value){
             if(typeof(value)=='string'){
                 if(/[^\d]/.test(value)  || 0 >= parseInt(value) || parseInt(value) >= 65535){
                     $scope.firewall_rule_port = true;
                 }else{
                     $scope.firewall_rule_port = false;
                 }

             }
         });
         $scope.$watch('firewall_rule.from',function(value){
             if(typeof(value)=='string'){
                 if(/[^\d]/.test(value) || 0 >= parseInt(value) || parseInt(value) >= 65535){
                     $scope.firewall_rule_form = true;
                 }else{
                     $scope.firewall_rule_form = false;
                 }
             }
         });
         $scope.$watch('firewall_rule.to',function(value){
             if(typeof(value)=='string'){
                 if(/[^\d]/.test(value) || 0 >= parseInt(value) || parseInt(value) >= 65535){
                     $scope.firewall_rule_to = true;
                 }else{
                     $scope.firewall_rule_to = false;
                 }
             }
         });

         $scope.create = function(firewall_rule){

             var post_data ={}
             if ($scope.selected_rule =='tcp' || $scope.selected_rule=='udp'){
                 if((firewall_rule.port_range =='port' && $.trim(firewall_rule.port)=='')){
                     $scope.firewall_rule_port = true;
                     return ;

                 }
                 if(firewall_rule.port_range=='range'){
                     if($.trim(firewall_rule.from)==''){
                         $scope.firewall_rule_form = true;
                         return ;
                     }
                     if($.trim(firewall_rule.to)==''){
                         $scope.firewall_rule_to = true;
                         return ;
                     }
                     if(parseInt(firewall_rule.from)>parseInt(firewall_rule.to)){
                         $scope.firewall_rule_to = true;
                         return ;
                     }
                 }
                 if(firewall_rule.port_range=='range'){
                     if(parseInt(firewall_rule.from) > parseInt(firewall_rule.to)){
                         $scope.firewall_rule_to = true
                         return
                     }
                 }
                 post_data = {
                     "firewall":$scope.firewall_id,
                     "direction":firewall_rule.direction ? firewall_rule.direction:'ingress',
                     "ether_type":'IPv4',
                     "port_range_min":firewall_rule.port_range=='port'?firewall_rule.port:firewall_rule.from,
                     "port_range_max":firewall_rule.port_range=='port'?firewall_rule.port:firewall_rule.to,
                     "protocol":$scope.selected_rule =='udp'? 'udp':'tcp'
                 }
             }else{
                 var select_data = eval("("+$scope.selected_rule+")");
                 post_data = {
                     "firewall":$scope.firewall_id,
                     "direction":'ingress',
                     "ether_type":'IPv4',
                     "port_range_min":select_data.from_port,
                     "port_range_max":select_data.to_port,
                     "protocol":select_data.ip_protocol
                 }
             }

             CommonHttpService.post("/api/firewall/firewall_rules/create/", post_data).then(function (data) {
                 if (data.OPERATION_STATUS == 1) {
                     ToastrService.success(data.MSG, $i18next("success"));
                     firewall_rules_table.reload();
                 }
                 else {
                     ToastrService.error(data.MSG, $i18next("op_failed"));
                 }
                 $modalInstance.dismiss();
             });
         }
     });
