/**
 * User: bluven
 * Date: 15-7-29 Time: 上午11:28
 */


'use strict';

CloudApp.controller('WorkflowManagementController',
    function ($rootScope, $scope, $i18next, $ngBootbox, $modal, lodash, ngTableParams,
              CommonHttpService, ToastrService, ngTableHelper, Workflow) {

        $scope.workflows = [];

        $scope.table = new ngTableParams({
            page: 1,
            count: 10
        },{
            counts: [],
            getData: function ($defer, params) {
                Workflow.query(function (data) {
                    $scope.workflows = ngTableHelper.paginate(data, $defer, params);
                });
            }
        });

         $scope.openWorkflowModal = function(workflow){

            workflow = workflow || {steps: [{}]};

            $modal.open({
                templateUrl: 'define.html',
                controller: 'WorkflowDefineController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    workflow: function(){
                        return workflow;
                    },
                    resourceTypes: function(CommonHttpService){
                        return CommonHttpService.get('/api/settings/resource_types/');
                    },
                    users: function(User){
                        return User.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.table.reload();
            });
        };

        $scope.setAsDefault = function(workflow){

            $ngBootbox.confirm($i18next("workflow.default_workflow_confirm")).then(function(){

                var params = {
                    id: workflow.id,
                    resource_type: workflow.resource_type
                };

                CommonHttpService.post("/api/workflows/set-default/", params).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.cancelDefault = function(workflow){

            $ngBootbox.confirm($i18next("workflow.cancel_default_confirm")).then(function(){

                CommonHttpService.post("/api/workflows/cancel-default/", {id: workflow.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.delete = function(workflow){
            $ngBootbox.confirm($i18next("workflow.confirm_delete")).then(function(){

                CommonHttpService.post("/api/workflows/delete/", {id: workflow.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };
    })

    .controller('WorkflowDefineController', function($rootScope, $scope, $i18next, lodash,
              CommonHttpService, ToastrService, ValidationTool,
              $modalInstance, workflow, users, resourceTypes){

        var form;

        workflow = angular.copy(workflow);
        $scope.workflow = workflow;
        $scope.users = users;
        $scope.resourceTypes = [];
        $scope.cancel = $modalInstance.dismiss;

        var init = function(){

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init("#workflowForm");
            });

            ValidationTool.addValidator('uniqueApprover', function(value, element){

                value = parseInt(value);
                var user = users[value];

                var countResult = lodash.chain(workflow.steps).map('approver').countBy(function(n){
                    return n;
                }).value();

                return countResult[user.id] == 1;

            }, $i18next('workflow.same_approver'));

            for(var attr in resourceTypes){
                $scope.resourceTypes.push({key: attr, label: resourceTypes[attr]});
            }
        };

        var switchSteps = function(i, j){

            var steps = workflow.steps;
            var tmp = steps[i];

            steps[i] = steps[j];
            steps[j] = tmp;
        };

        $scope.up = function(index){
            switchSteps(index, index - 1);
        };

        $scope.down = function(index){
            switchSteps(index, index + 1);
        };

        $scope.insertAfter = function(step){

            var steps = workflow.steps;
            var length = steps.length;

            for(var i = 0 ; i < length; i++){
                if(steps[i] == step){
                    steps.splice(i+1, 0, {});
                    break;
                }
            }
        };

        $scope.removeStep = function(step){
            var steps = workflow.steps;
            var length = steps.length;

            for(var i = 0 ; i < length; i++){
                if(steps[i] == step){
                    steps.splice(i, 1);
                }
            }
        };

        $scope.submit = function(){

            if(form.valid() == false){
                return;
            }

            var params = {
                id: workflow.id,
                name: workflow.name,
                resource_type: workflow.resource_type,
                step_ids: [],
                step_names: [],
                step_approvers: []
            };

            angular.forEach(workflow.steps, function(step){
                params.step_ids.push(step.id);
                params.step_names.push(step.name);
                params.step_approvers.push(step.approver);
            });

            CommonHttpService.post('/api/workflows/define/', params)
                .then(function(result){

                if (result.success) {
                    ToastrService.success(result.msg, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(result.msg, $i18next("op_failed"));
                }
            });
        };

        init();
    });
