'use strict';

CloudApp.controller('ForumController',
    function($rootScope, $scope, $interval, $i18next, ForumReply,
             CommonHttpService, ToastrService) {

    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
        loadForums();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;

    $scope.forum_list = [];
    $scope.forum_reply_list = [];
    $scope.reply_content = '';

    var loadForums = function(){
        CommonHttpService.get('/api/forums/').then(function(data){
            $scope.forum_list =  data;

            if($scope.current_forum == undefined){
                $scope.current_forum = data[0];
                $scope.load_replies($scope.current_forum);
            }
        });
    };

    var stopLoadForums = $interval(loadForums, 10000);
    $scope.$on('$destroy', function () {
        $interval.cancel(stopLoadForums);
    });

    $scope.load_replies = function(forum){
        $scope.current_forum = forum;
        $scope.forum_reply_list = ForumReply.query({forum_id: forum.id});
    };

    $scope.close_forum = function(forum){
        bootbox.confirm($i18next("forum.confirm_close"), function (confirm) {
            if (confirm) {
                var post_data={
                    "id":forum.id
                };

                CommonHttpService.post("/api/forums/close/", post_data).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        $scope.current_forum = data.data;
                        loadForums();
                    } else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                });
            }
        });
    };

    $scope.reply = function(forum, reply_content){
        var post_data = {
            "reply_content":reply_content,
            "forum": forum.id
        };

        CommonHttpService.post("/api/forums/reply/create/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                $scope.load_replies(forum);
                $scope.reply_content = '';
            } else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }
        });
    };
});
