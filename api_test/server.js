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
		'query_robots_configuration':query_robots_configuration,
		'modify_file_lock':modify_file_lock,
		'query_ftp_port':query_ftp_port,
		'get_file':get_file,
		'update_ntp_server':update_ntp_server,
		'query_progress_info':query_progress_info,
		'setting_process_state':setting_process_state,
		'query_robot_process_info':query_robot_process_info
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

	function QueryRobotList (user_id) {
		return RequestJsonData(JSON.stringify({'event': 'get_online_robot_list','user_id':parseInt(user_id)}))
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

	function modify_file_lock(opecode,robot1){
		return RequestJsonData(JSON.stringify({'event': 'event_modify_file_lock', 'opcode': parseInt(opecode),'robot_list':[parseInt(robot1)]}))
	}

	function query_ftp_port(){
		return RequestJsonData(JSON.stringify({'event': 'event_query_ftp_port'}))
	}

	function update_ntp_server(robot1,ntp_server){
		return RequestJsonData(JSON.stringify({'event': 'event_update_ntp_server','robot_list':[parseInt(robot1)],'ntp_host':ntp_server}))
	}

	function query_progress_info(user_id){
		return RequestJsonData(JSON.stringify({'event': 'event_query_progress_info','user_id':parseInt(user_id)}))
	}

	function setting_process_state(robot_id,command){
		return RequestJsonData(JSON.stringify({'event': 'event_operate_system_process','robot_list':[parseInt(robot_id)],'command':parseInt(command)}))
	}

	function query_robot_process_info(robot_id){
		return RequestJsonData(JSON.stringify({'event': 'event_query_robot_process_list','robot_id':parseInt(robot_id)}))
	}

	function get_file(){
		
		return Downer(url+'/download/jquery-3.3.2.zip/user_id=2,type=1')

		// return Downer(url+'/download/jquery-3.3.1.zip')
		// return GetData(url+'/download/jquery-3.3.1.zip')
	}
		http://192.168.5.121:5010/download/jquery-3.3.3.zip/user_id=2,type=1

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

	function GetData(request_url,data){
		var defer = $q.defer();
		$http({
			method:'GET',
			url:request_url,
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