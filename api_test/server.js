app.service('$http_services',['$http','$q',function($http,$q){
	return {
		'RequestRobotDetailInfo': RequestRobotDetailInfo,
		'RequestRobotSystemInfo': RequestRobotSystemInfo,
		'Login': Login,
		'LoginOut': LoginOut,
		'QueryRobotList': QueryRobotList,
		'load_navigation': load_navigation,
		'load_vehicle': load_vehicle,
		'load_operation': load_operation,
		'load_optpar': load_optpar,
		'load_varlist': LoadVarlist,
		'load_vardata': LoadVardata,
		'ClearError': ClearError,
		'StopEmergency': StopEmergency,
		'QueryPackets':QueryPackets,
		'QueryUser':QueryUser,
		'RobotUpgrade':RobotUpgrade,
		'query_transfer_queue':query_transfer_queue,
		'cancle_task':cancle_task,
		'query_robots_configuration':query_robots_configuration
	}

	function RequestRobotDetailInfo (RobotId) {
		var json = {'event': 'get_robot_detail_info', 'robot_id': RobotId}
		return RequestJsonData(JSON.stringify(json))
	}

	function RequestRobotSystemInfo (RobotId) {
		var json = {'event': 'get_robot_system_info', 'robot_id': RobotId}
		return RequestJsonData(JSON.stringify(json))
	}

	function Login (user, password) {
		return RequestJsonData(JSON.stringify({'event': 'event_login', 'user_name': user, 'password': password}))
	}

	function LoginOut (uid) {
		return RequestJsonData(JSON.stringify({'event': 'event_logout', 'user_id': uid}))
	}

	function QueryRobotList () {
		return RequestJsonData(JSON.stringify({'event': 'get_online_robot_list'}))
	}

	function load_navigation (robot_id) {
		return RequestHtmlData(JSON.stringify({'event': 'load_navigation', 'robot_id': robot_id}))
	}

	function load_vehicle (robot_id) {
		return RequestHtmlData(JSON.stringify({'event': 'loadvehicle', 'robot_id': robot_id}))
	}

	function load_operation (robot_id) {
		return RequestHtmlData(JSON.stringify({'event': 'load_operation', 'robot_id': robot_id}))
	}

	function load_optpar (robot_id) {
		return RequestHtmlData(JSON.stringify({'event': 'load_optpar', 'robot_id': robot_id}))
	}

	function LoadVarlist (robot_id) {
		return RequestJsonData(JSON.stringify({'event': 'load_varlist', 'robot_id': robot_id}))
	}

	function LoadVardata (robot_id,varId,typeId) {
		return RequestJsonData(JSON.stringify({'event': 'load_vardata', 'robot_id': robot_id, 'var_id':varId,'type_id':typeId}))
	}

	function ClearError (robot_id) {
		return RequestJsonData(JSON.stringify({'event': 'clear_error', 'robot_id': robot_id}))
	}

	function StopEmergency (robot_id) {
		return RequestJsonData(JSON.stringify({'event': 'stop_emergency', 'robot_id': robot_id}))
	}

	function QueryPackets(user_id) {
		return RequestJsonData(JSON.stringify({'event': 'event_packages', 'user_id': user_id}))
	}

	function QueryUser() {
		return RequestJsonData(JSON.stringify({'event': 'event_users'}))
	}

	function cancle_task(user_id,robot_id,task_id1){
		return RequestJsonData(JSON.stringify({'event': 'cancle_file_transform_task', 'user_id': parseInt(user_id),'robot_id':parseInt(robot_id),'task_list':[task_id1]}))
	}

	function RobotUpgrade(userId,packetId,Robotid1,Robotid2) {
		robot_list = [];
		robot_list.push(parseInt(Robotid1));
		robot_list.push(parseInt(Robotid2));
		return RequestJsonData(JSON.stringify({'event': 'event_robot_upgrade','robot_list':robot_list,'package_id':parseInt(packetId),"user_id":parseInt(userId)}))
	}

	function query_robots_configuration(userId){
		return RequestJsonData(JSON.stringify({'event': 'query_robots_configuration_info','user_id':parseInt(userId)}))
	}

	function query_transfer_queue(userId,type){
		return RequestJsonData(JSON.stringify({'event': 'query_user_transfer_queue', 'user_id': parseInt(userId),'file_type':parseInt(type)}))
	}

	function 	RequestJsonData(data){
		var defer = $q.defer();
		$http({
			method:'POST',
			url:url,
			data:data,
			dataType: "json"
		}).then(function successCallback(response) {
			defer.resolve(response.data);
		}, function errorCallback(error) {
			defer.reject(error);
		});
		return defer.promise;
	}

	function RequestHtmlData(data){
		var defer = $q.defer();
		$http({
			method:'POST',
			url:url,
			data:data,
			dataType: "html"
		}).then(function successCallback(response) {
			defer.resolve(response.data);
		}, function errorCallback(error) {
			defer.reject(error);
		});
		return defer.promise;
	}
}])