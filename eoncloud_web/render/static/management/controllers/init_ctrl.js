/**
 * User: bluven
 * Date: 15-7-7
 * Time: 下午5:45
 */
CloudApp.controller('InitWizardController',
    function($rootScope, $scope, $i18next, $timeout, $window,
             CommonHttpService, ToastrService,
             InitWizard, InitWizardValidator){

        var wizard = null,
            validator = null,
            FLAVOR_TEMPLATE = {name: '', cpu: 0, memory: 0, price: 0.0 },
            data_center = $scope.data_center = {auth_url: 'http://'},
            flavors = $scope.flavors = [angular.copy(FLAVOR_TEMPLATE)],
            images = $scope.images = [{}];

        $scope.$on('$includeContentLoaded', function(){
                Metronic.initAjax();
                wizard = InitWizard.init();
                validator = InitWizardValidator.init();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;
        $scope.step = 'data_center';
        $scope.os_types = [{key: 1, label: 'Windows'}, {key: 2, label: 'Linux'}];

        $scope.createDataCenter = function(){

            if(validator.isDataCenterValid() == false){
                return;
            }

            CommonHttpService.post('/api/init/data_center/',
                    $scope.data_center).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $scope.step = 'flavor';
                    wizard.bootstrapWizard('next');
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };

        $scope.createFlavors = function(){

            if(validator.isFlavorValid() == false){
                return;
            }

            var params = {names: [], cpus: [], memories: [], prices: []};

            angular.forEach(flavors, function(flavor){
                params.names.push(flavor.name);
                params.cpus.push(flavor.cpu);
                params.memories.push(flavor.memory);
                params.prices.push(flavor.price);
            });

            CommonHttpService.post('/api/init/flavors/', params).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $scope.step = 'image';
                    wizard.bootstrapWizard('next');
                } else {
                    bootbox.dialog({
                        'title': $i18next("failed"),
                        message: $i18next("init_wizard.flavor_create_failed")
                    });
                }
            });
        };

        $scope.skip = function(){
            $scope.step = 'image';
            wizard.bootstrapWizard('next');
        };

        $scope.createImages = function(){

            if(validator.isImageValid() == false){
                return;
            }

            var params = {names: [], login_names: [], uuids: [], os_types: []};
            angular.forEach(images, function(image){
                params.names.push(image.name);
                params.login_names.push(image.login_name);
                params.uuids.push(image.uuid);
                params.os_types.push(image.os_type);
            });

            CommonHttpService.post('/api/init/images/', params).then(function(data){
                if (data.success) {
                    $timeout(function(){
                        $window.location.reload();
                    }, 5000);

                    $scope.step = 'final';
                    bootbox.dialog({
                        'title': $i18next("success"),
                        message: $i18next("init_wizard.image_create_success")
                    });

                } else {
                    bootbox.dialog({
                        'title': $i18next("failed"),
                        message: $i18next("init_wizard.image_create_failed")
                    });
                }
            });
        };

        $scope.addFlavor = function(){
            flavors.push(angular.copy(FLAVOR_TEMPLATE));
        };

        $scope.removeFlavor = function(targetIndex){
            var retainedFlavors = [];
            for(var i = 0; i < flavors.length; i++){
                if (i != targetIndex){
                   retainedFlavors.push(flavors[i]);
                }
            }

            flavors = $scope.flavors = retainedFlavors;
        };

        $scope.addImage = function(){
            images.push({});
        };

        $scope.removeImage = function(targetIndex){
            var retainedImages = [];
            for(var i = 0; i < images.length; i++){
                if (i != targetIndex){
                   retainedImages.push(images[i]);
                }
            }

            images = $scope.images = retainedImages;
        };
    })
    .factory('InitWizard', function (){

        var handleTitle = function(tab, navigation, index) {

            var total = navigation.find('li').length;
            // set wizard title
            $('.step-title', $('#cloud-wizard')).text((index + 1) + ' / ' + total);
            // set done steps
            jQuery('li', $('#cloud-wizard')).removeClass("done");
            var li_list = navigation.find('li');
            for (var i = 0; i < index; i++) {
                jQuery(li_list[i]).addClass("done");
            }

            Metronic.scrollTo($('.page-title'));
        };

        var init = function(){

            if (!jQuery().bootstrapWizard) {
                return;
            }

            // default form wizard
            $('#cloud-wizard').bootstrapWizard({
                onTabClick: function () { return false; },
                onNext: function (tab, navigation, index) {
                    handleTitle(tab, navigation, index);
                },
                onTabShow: function (tab, navigation, index) {
                    var total = navigation.find('li').length;
                    var current = index + 1;
                    var $percent = (current / total) * 100;
                    $('#cloud-wizard').find('.progress-bar').css({
                        width: $percent + '%'
                    });
                }
            });
            return $("#cloud-wizard");
        };

        return {init: init}
    }).factory('InitWizardValidator',
        ['$i18next', 'ValidationTool', function ($i18next, ValidationTool){

        var dataCenterRules = {
                data_center_name: {
                    minlength: 2,
                    maxlength: 128,
                    required: true
                },
                host: {
                    required: true,
                    ip: true,
                    remote: {
                        url: "/api/data-centers/is-host-unique",
                        data: {},
                        async: false
                    }
                },
                project: {
                    required: true,
                    minlength: 2,
                    maxlength: 128
                },
                user: {
                    required: true,
                    minlength: 2,
                    maxlength: 128
                },
                password: {
                    required: true,
                    minlength: 2,
                    maxlength: 50
                },
                auth_url: {
                    required: true,
                    url: true
                },
                ext_net: {
                    required: true,
                    minlength: 2,
                    maxlength: 128
                }
            };

        var config = { rules: dataCenterRules};

        return {init: function(){
            var forms = {
                dataCenterForm: ValidationTool.init("#dataCenterForm", config),
                flavorForm: ValidationTool.init("#flavorForm"),
                imageForm: ValidationTool.init("#imageForm"),
                valid: function(){
                    return this.dataCenterForm.valid() && this.flavorForm.valid() && this.imageForm.valid();
                },
                isDataCenterValid: function(){ return this.dataCenterForm.valid(); },
                isFlavorValid: function(){ return this.flavorForm.valid();},
                isImageValid: function(){ return this.imageForm.valid();}
            };

            return forms;
        }};

    }]);