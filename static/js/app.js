/**
 * Created by jiangweiwei on 16/11/29.
 */

angular.module('WebApp', ['ui.router', 'ngResource', 'WebCtr', 'WebService', 'ngCookies']);

angular.module('WebApp')
.config(function($stateProvider,$httpProvider){
    $stateProvider.state('DataList',{
        url:'/DataList',
        templateUrl:'../static/partials/DataList.html',
        controller:'DataListCtr'
    }).state('EditData',{
        url:'/DataList/:id/edit',
        templateUrl:'../static/partials/EditData.html',
        controller:'EditCtr'
    }).state('AddData',{
        url:'/DataList/AddData',
        templateUrl:'../static/partials/DataAdd.html',
        controller:'AddCtr'
    }).state('AddVersion',{
        url:'/DataList/AddVersion',
        templateUrl:'../static/partials/AddAppVersion.html',
        controller:'Add_version'
    }).state('Login',{
        url:'/Login',
        templateUrl:'../static/partials/Login.html',
        controller:'LoginCtr'
    }).state('LogServer',{
        url:'/log',
        templateUrl:'../static/partials/log.html',
        controller:'LogCtr'
    });
}).run(function($state, $rootScope, $http, $cookieStore, AuthService){
    //初始化全局函数
    $rootScope.AppVersion = '';
    $rootScope.event = '';
    $rootScope.platform = '';
    $rootScope.page = '';
    $rootScope.page_key = '';
    $rootScope.currentPage = 1;
    $rootScope.username = '';
    $rootScope.userrole = '';
    $rootScope.globals = AuthService.get({}, function () {
        if ($rootScope.globals.is_login) {
        $rootScope.username = $rootScope.globals.username;
        $rootScope.role = $rootScope.globals.role;
        $state.go('DataList')
    }
        else {
            $state.go('Login');
        }
    });


    $rootScope.$on('stateChangeStart', function (event, toState, fromState, AuthService) {
        status = AuthService.get({}, function () {
            if (toState.name != 'Login' && !status.is_login){
            $state.go('Login');
        }
            else {
                $rootScope.username = status.username;
                $rootScope.role = status.role;
            }
        });

    })
});