'use strict';

CloudApp.controller('ForumController',
    function($rootScope, $scope, $interval, $i18next, ForumReply,
             CommonHttpService, ToastrService) {

    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
        loadForums();
    });

    $scope.forum_list = [];
    $scope.forum_reply_list = [];

    var replyForm = $scope.replyForm = {
        content: '',
        submit:  function(){
            var post_data = {
                "reply_content": this.content,
                "forum": $scope.current_forum.id
            };

            CommonHttpService.post("/api/forums/reply/create/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    $scope.loadReplies($scope.current_forum);
                    replyForm.content = '';
                } else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
            });
        }
    };

    var loadForums = function(){
        CommonHttpService.get('/api/forums/').then(function(data){
            $scope.forum_list =  data;

            if(data.length > 0){
                $scope.current_forum = data[0];
                $scope.loadReplies($scope.current_forum);
            } else {
                $scope.current_forum = null;
                $scope.forum_reply_list = [];
            }
        });
    };

    $rootScope.setInterval(loadForums, 10000);

    $scope.loadReplies = function(forum){

        if(forum == undefined){
            return;
        }

        $scope.current_forum = forum;
        $scope.forum_reply_list = ForumReply.query({forum_id: forum.id});
    };

    $scope.close_forum = function(forum){
        bootbox.confirm($i18next("forum.confirm_close"),
            function(confirmed){

                if (!confirmed) {
                    return;
                }

                CommonHttpService.post("/api/forums/close/", {'id': forum.id}).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        $scope.current_forum = data.data;
                    } else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                });
        });
    };
});
