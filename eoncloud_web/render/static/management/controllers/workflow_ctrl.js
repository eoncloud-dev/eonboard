/**
 * User: bluven
 * Date: 15-7-29 Time: 上午11:28
 */


'use strict';

CloudApp.controller('InstanceCreateFlowController',
    function ($rootScope, $scope, $i18next, lodash,
              CommonHttpService, ToastrService, ValidationTool,
              users, workflow) {

        var form;

        function init(){

            $scope.workflow = workflow;
            $scope.users = users;

            if(workflow.steps.length == 0){
                workflow.steps.push({});
            }

            ValidationTool.addValidator('uniqueAuditor', function(value, element){

                value = parseInt(value);
                var user = users[value];

                var countResult = lodash.chain(workflow.steps).map('auditor').countBy(function(n){
                    return n;
                }).value();

                return countResult[user.id] == 1;

            }, $i18next('workflow.same_auditor'));

            $scope.$on('$viewContentLoaded', function () {
                Metronic.initAjax();
                form = ValidationTool.init("#workflowForm");
            });

            $rootScope.settings.layout.pageBodySolid = true;
            $rootScope.settings.layout.pageSidebarClosed = false;

        }

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
                workflow_id: workflow.id,
                step_ids: [],
                step_names: [],
                step_auditors: []
            };

            angular.forEach(workflow.steps, function(step){
                params.step_ids.push(step.id);
                params.step_names.push(step.name);
                params.step_auditors.push(step.auditor);
            });

            CommonHttpService.post('/api/workflows/instance-create/update/', params)
                .then(function(result){

                if (result.success) {
                    ToastrService.success(result.msg, $i18next("success"));
                    workflow = $scope.workflow = result.data;
                } else {
                    ToastrService.error(result.msg, $i18next("op_failed"));
                }
            });
        };

        init();
    });
