/**
 * User: bluven
 * Date: 15-7-31 Time: 下午4:06
 */

'use strict';

CloudApp.controller('MyWorkflowController',
    function ($rootScope, $scope, $i18next, $modal, ngTableParams,
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
            count: 5
        },{
            counts: [],
            getData: function ($defer, params) {
                FlowInstance.query({role: 'applier'}, function (data) {
                    $scope.instances = ngTableHelper.paginate(data, $defer, params);
                });
            }
        });

        var isRejected = $scope.isRejected = function(instance){
           return instance.is_complete && instance.reject_reason;
        };

        $scope.stepClass = function(instance, step){

            var clazz = ['label'],
                currentStep = instance.current_step;

            if(currentStep.order > step.order){
               clazz.push('label-success');
            }

            if(currentStep.order < step.order){
                clazz.push('label-default');
            }

            if(currentStep.order == step.order){

                if(instance.is_complete){

                    if(instance.reject_reason){
                        clazz.push('label-danger');
                    } else {
                        clazz.push('label-success');
                    }
                }  else {
                    clazz.push('label-primary');
                }
            }

            return clazz;
        };

        $scope.endStepClass = function(instance){

            if(isRejected(instance) || !instance.is_complete){
                return ['label', 'label-default'];
            }

            if(instance.is_complete){
               return ['label', 'label-success'];
            }
            return [];
        };
    });