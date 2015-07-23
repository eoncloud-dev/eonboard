'use strict';


CloudApp.controller('InstanceDetailController',
    function ($rootScope, $scope, $filter, $timeout, ngTableParams,CommonHttpService, instance,status_desc) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.instance = instance;
        $scope.status_desc = status_desc;

        $scope.log_load_status = false;
        // load instance log
        $scope.load_instance_log = function(instance_id){
            if(!$scope.log_load_status){
                Metronic.blockUI({
                    target: '#instance_log',
                    animate: true
                });
                CommonHttpService.get('/api/instances/details/'+instance_id+"/?tag=instance_log").then(function(data){
                    $scope.instance_log = data;
                    Metronic.unblockUI('#instance_log');
                    $scope.log_load_status = true;
                });
            }
        }
    });
