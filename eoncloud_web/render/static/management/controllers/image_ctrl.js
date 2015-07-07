/**
 * User: bluven
 * Date: 15-7-3
 * Time: 上午9:49
 */

CloudApp.controller('ImageController',
    function($rootScope, $scope, $filter, $modal, $i18next,
             CommonHttpService, ToastrService, ngTableParams,
             Image, CheckboxGroup){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.images = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.images);

        $scope.image_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function ($defer, params) {
                    Image.query(function (data) {
                        var results = $filter('orderBy')(data, params.orderBy());
                        params.total(results.length);
                        $scope.images = results.slice((params.page() - 1) * params.count(), params.page() * params.count());
                        $defer.resolve($scope.images);
                        checkboxGroup.syncObjects($scope.images);
                    });
                }
            });

        $scope.edit = $scope.create = function(image) {

                image = image || {};

                $modal.open({
                    templateUrl: 'create.html',
                    controller: 'ImageCreateController',
                    backdrop: "static",
                    size: 'lg',
                    resolve: {
                        image_table: function () {
                            return $scope.image_table;
                        },
                        image: function(){return image;}
                    }
                });
            };

        var deleteImages = function(ids){

            bootbox.confirm($i18next("image.confirm_delete"), function(confirmed){

                if(!confirmed){
                    return;
                }

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/images/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.image_table.reload();
                        checkboxGroup.uncheck();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteImages(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(image){
                    if(image.checked){
                        ids.push(image.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(image){
            deleteImages([image.id]);
        };
    })

    .controller('ImageCreateController',
        function($rootScope, $scope, $modalInstance,
                 image_table, image, Image, User, DataCenter, ImageForm,
                 $i18next, CommonHttpService, ResourceTool, ToastrService){

            $scope.users = User.query();
            $scope.data_centers = DataCenter.query();
            $scope.image = ResourceTool.copy_only_data(image);
            $scope.os_types = [{key: 1, label: 'Windows'}, {key: 2, label: 'Linux'}];

            $modalInstance.opened.then(function() {
                setTimeout(ImageForm.init, 0);
            });

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

            $scope.submit = function(image){

                if(!$("#imageForm").valid()){
                    return;
                }

                var url = '/api/images';

                if(image.id){
                    url += "/update/";
                } else {
                    url += "/create/";
                }

                CommonHttpService.post(url, image).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        image_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
    ).factory('ImageForm', ['ValidationTool', function (ValidationTool) {
        return {
            init: function(){

                var config = {
                    rules: {
                        name: {
                            minlength: 2,
                            maxlength: 50,
                            required: true
                        },
                        os_type: 'required',
                        login_name: 'required',
                        data_center: 'required'
                    }
                };

                return ValidationTool.init('#imageForm', config);
              }
            }
        }]);