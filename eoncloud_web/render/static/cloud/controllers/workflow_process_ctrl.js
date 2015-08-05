/**
 * User: bluven
 * Date: 15-7-31 Time: 上午11:12
 */



'use strict';

CloudApp.controller('WorkflowProcessController',
    function ($rootScope, $scope, $i18next, $ngBootbox,
              $modal, ngTableParams,
              CommonHttpService, ToastrService,
              ngTableHelper, FlowInstance) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.instances = [];

        $scope.table = new ngTableParams({
            page: 1,
            count: 10
        },{
            counts: [],
            getData: function ($defer, params) {
                FlowInstance.query({role: 'approver'}, function (data) {
                    $scope.instances = ngTableHelper.paginate(data, $defer, params);
                });
            }
        });

        $scope.reject = function(instance){
            $modal.open({
               templateUrl: 'reject.html',
                backdrop: "static",
                controller: 'RejectFlowController',
                size: 'lg',
                resolve: {
                    instance: function(){
                        return instance;
                    }
                }
            }).result.then(function(){
               $scope.table.reload();
            });
        };

        $scope.approve = function(instance){

            var msg = $i18next("workflow.confirm_approve", {applier: instance.owner_name});

            $ngBootbox.confirm(msg).then(function(){
                CommonHttpService.post(
                '/api/workflow-instances/approve/', {id: instance.id}).then(function(result){
                     if (result.success) {
                        ToastrService.success(result.msg, $i18next("success"));
                         $scope.table.reload();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            });
        };
    })

    .controller('RejectFlowController', function($scope, $i18next,
                                                 ToastrService, CommonHttpService, ValidationTool,
                                                 $modalInstance,  instance){
        var form;
        $scope.reason = '';
        $scope.cancel = $modalInstance.dismiss;

        $modalInstance.rendered.then(function(){
            form = ValidationTool.init("#rejectForm");
        });

        $scope.submit = function(){

            if(form.valid() == false){
                return;
            }

            CommonHttpService.post(
                '/api/workflow-instances/rejected/',
                {id: instance.id, reason: $scope.reason}).then(function(result){
                     if (result.success) {
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
        };
    });