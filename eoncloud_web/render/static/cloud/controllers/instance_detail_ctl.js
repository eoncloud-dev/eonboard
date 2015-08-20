'use strict';


CloudApp.controller('InstanceDetailController',
    function ($rootScope, $scope, $sce, $interpolate,
              CommonHttpService, DatePicker, InstanceState,
              instance, monitorSettings) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        InstanceState.process(instance);
        $scope.instance = instance;
        $scope.monitorSettings = monitorSettings;
        $scope.monitorIntervals = monitorSettings.intervals;
        $scope.monitors = monitorSettings.monitors;

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
        };
    })
    .directive('eonMonitor', function(){

        var controller = function($scope, $sce, $interpolate){

            var uuid = $scope.uuid,
                urlTemplate = $scope.url;

            $scope.mode = 'quick';

            var currentConfig = {
                    uuid: uuid,
                    interval: 'second',
                    mode:'quick',
                    from: 'now-1h',
                    to: 'now'
                },
                cancelWatchTimeRange = null,
                format = 'YYYY-MM-DD',
                iso8601Format = 'YYYY-MM-DDTHH:mm:ss.SSS';

            urlTemplate = $interpolate(urlTemplate + '&_g=(time:(from:{[{ from }]},mode:{[{ mode }]},to:{[{ to }]}))');

            $scope.changeInterval = function(interval){
                currentConfig.interval = interval;
                loadMonitor();
            };

            var loadMonitor = function(){
                var url = "/api/instances/monitor" + urlTemplate(currentConfig);
                $scope.monitorUrl = $sce.trustAsResourceUrl(url);
            };

            $scope.changeMode = function(mode){

                currentConfig.mode = $scope.mode = mode;

                if(mode == 'quick'){
                    currentConfig.from = 'now-1h';
                    currentConfig.to = 'now';
                    if(cancelWatchTimeRange){
                        cancelWatchTimeRange();
                    }
                } else if(mode == 'absolute') {

                    $scope.timeRange = {
                        from: moment().format(format),
                        to: moment().format(format)
                    };

                    var cancelWatchFrom = $scope.$watch('timeRange.from', function(newValue){
                        currentConfig.from = "'" + moment(newValue, format).utc().format(iso8601Format) + "Z'";
                        loadMonitor();
                    });

                    var cancelWatchTo = $scope.$watch('timeRange.to', function(newValue){
                        // With one more day added, this range will include end day totally,
                        // for example, 2015-07-01~2015-07-02, without adding one day,
                        // this range in fact only range from 2015-07-01 00:00:00 ~ 2015-07-02 00:00:00,
                        // after adding one day, this range is from 2015-07-01 00:00:00 ~ 2015-07-02 24:00:00
                        var to = moment(newValue, format).add(1, 'day');
                        currentConfig.to = "'" + to.utc().format(iso8601Format) + "Z'";
                        loadMonitor();
                    });

                    cancelWatchTimeRange = function(){
                        cancelWatchFrom();
                        cancelWatchTo();
                    }
                }
            };

            loadMonitor();
        };

        return {
            restrict: 'A',
            templateUrl: '/static/cloud/views/monitor_partial.html',
            scope: {
                uuid: '=',
                title: '=',
                intervals: '=',
                url: '='
            },
            controller: controller,
            link: function(scope, element, attrs){
                element.find('.date-picker').datepicker({
                    rtl: Metronic.isRTL(),
                    orientation: "left",
                    format: 'yyyy-mm-dd',
                    autoclose: true
                });
            }
        }
    });
