var app = angular.module('Api_Test', []);
var url = "";
app.controller('Api_controller', function($scope,$http_services,$interval) {
    var socket = null;
    var namespace = '/notify_call';
    var init = true;
    $scope.Ip = "172.20.10.3";
    $scope.Port = "5008";
    $scope.disabled = true;
    $scope.bconnected = false;
    $scope.disabled_socketio = false;
    var updateinfo = "";

    url = 'http://' + $scope.Ip + ':' + $scope.Port ;

    $scope.$watch('Port + Ip', function(newValue, oldValue){
        if(newValue === oldValue){
            return ;
        }
        url = 'http://' + $scope.Ip + ':' + $scope.Port ;

        if($scope.Ip && $scope.Port && $scope.test_api ){
            $scope.disabled = false;
        }
        else{
            $scope.disabled = true;
        }

        if($scope.Ip && $scope.Port){
            $scope.disabled_socketio = false;
        }
        else{
            $scope.disabled_socketio = true;
        }
    });

    $scope.select_change = function(){
        if($scope.Ip && $scope.Port && $scope.test_api ){
            $scope.disabled = false;
        }
        else{
            $scope.disabled = true;
        }
    }

    //event: 展示给用户
    //args： 函数参数 需要和函数参数对应
    //param ：与args 参数个数对应，有几个参数 写几个NULL
    //function：在server.js中执行的函数 json主键
    //type: 1表示请求json类型 0 表示请求html 类型
    $scope.api_list = [
    {'event':'event_login','args':['user','name'],'param':[null,null],'function':'Login','type':1},
    {'event':'event_logout','args':['uid'],'param':[null],'function':'LoginOut','type':1},
    {'event':'get_online_robot_list','args':[],'param':[],'function':'QueryRobotList','type':1},
    {'event':'get_robot_detail_info','args':['robot_id'],'param':[null],'function':'RequestRobotDetailInfo','type':1},
    {'event':'get_robot_system_info','args':['robot_id'],'param':[null],'function':'RequestRobotSystemInfo','type':1},
    {'event':'load_navigation','args':['robot_id'],'param':[null],'function':'load_navigation','type':0},
    {'event':'loadvehicle','args':['robot_id'],'param':[null],'function':'load_vehicle','type':0},
    {'event':'load_operation','args':['robot_id'],'param':[null],'function':'load_operation','type':0},
    {'event':'load_optpar','args':['robot_id'],'param':[null],'function':'load_optpar','type':0},
    {'event':'load_varlist','args':['robot_id'],'param':[null],'function':'load_varlist','type':1},
    {'event':'load_vardata','args':['robot_id','var_id','type_id'],'param':[null,null,null],'function':'load_vardata','type':1},
    {'event':'clear_error','args':['robot_id'],'param':[null],'function':'ClearError','type':1},
    {'event':'stop_emergency','args':['robot_id'],'param':[null],'function':'StopEmergency','type':1},
    {'event':'event_packages','args':['user_id'],'param':[null],'function':'QueryPackets','type':1},
    {'event':'event_users','args':[],'param':[],'function':'QueryUser','type':1},
    {'event':'RobotUpgrade','args':['userId','packetId','Robotid1','Robotid2'],'param':[null,null,null,null],'function':'RobotUpgrade','type':1},
    {'event':'query_user_transfer_queue','args':['userId','type'],'param':[null,null],'function':'query_transfer_queue','type':1},
    {'event':'cancle_task','args':['userId','robot_id','task_id'],'param':[null,null,null],'function':'cancle_task','type':1},
    {'event':'query_robots_configuration_info','args':['userId'],'param':[null],'function':'query_robots_configuration','type':1},
    ]

    $scope.submit = function( api_param ){
        if(api_param.function){
            if(api_param.args.length> 0){
                $http_services[api_param.function].apply(this,api_param.param).then(
                    function(response){
                        success_callback(response,api_param.type);
                    },
                    function(error){
                        success_callback(error);
                    }
                );
            }
            else{
                $http_services[api_param.function]().then(
                    function(response){
                        success_callback(response,api_param.type);
                    },
                    function(error){
                        success_callback(error);
                    }
                );
            }
        }
    }

    function success_callback(data,type) {
        if(1 === type){
            $scope.result = JSON.stringify(data);
        }
        else{
            $("#template").html(data);
        }
        
    }

    function socket_response(data) {
        $scope.socket = JSON.stringify(json);
    }

    $scope.connect = function(){
        if(!socket){
            if(init){
                socket = io.connect(url + namespace);
                init = false;
            }
            else{
                socket = io.connect(url + namespace);
            }
            
            $scope.bconnected = true;
            socket.on('server_response', function(res) {
                updateinfo +=JSON.stringify(res) + '\r\n';
                
            });
        }
    }

    var timer = $interval(function(){
        if(updateinfo){
            $scope.socket +=updateinfo;
            updateinfo = "";
        }
    },1000);

    $scope.disconnect = function(){
        if(socket){
            socket.disconnect();
            socket = null;
            $scope.bconnected = false;
        }
    }
})