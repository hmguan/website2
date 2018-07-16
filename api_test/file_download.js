/**
 * Javascript 多文件下载
 * @author Barret Lee
 * @email  barret.china@gmail.com
 */
 var Downer = (function(files){
 	var queue_index_;
 	var h5Down = !/Trident|MSIE/.test(navigator.userAgent);
 	var downer ;
 	var queue_files_;
 	function downloadFile(fileName, contentOrPath){
 		var aLink = document.createElement("a");
 		evt = document.createEvent("MouseEvents");
 		isData = contentOrPath.slice(0, 5) === "data:";
 		isPath = contentOrPath.lastIndexOf(".") > -1;

		// 初始化点击事件
		// 注：initEvent 不加后两个参数在FF下会报错
		evt.initEvent("click",false,false);

		// 添加文件下载名
		aLink.download = fileName;

		// 如果是 path 或者 dataURL 直接赋值
		// 如果是 file 或者其他内容，使用 Blob 转换
		aLink.href = isPath || isData ? contentOrPath
		: URL.createObjectURL(new Blob([contentOrPath]));

		aLink.dispatchEvent(evt);
	};

	function IEdownloadFile(fileName, contentOrPath, bool){
		var isImg = contentOrPath.slice(0, 10) === "data:image",
		ifr = document.createElement('iframe');

		ifr.style.display = 'none';
		ifr.src = contentOrPath;

		document.body.appendChild(ifr);

		// dataURL 的情况
		isImg && ifr.contentWindow.document.write("<img src='" + 
			contentOrPath + "' />");

		if(bool){
			ifr.contentWindow.document.execCommand('SaveAs', false, fileName);
			document.body.removeChild(ifr);
		} else {
			setTimeout(function(){
				ifr.contentWindow.document.execCommand('SaveAs', false, fileName);
				document.body.removeChild(ifr);
			}, 0);
		}
	};

	function parseURL(str){
		return str.lastIndexOf("/") > -1 ? str.slice(str.lastIndexOf("/") + 1) : str;
	};

	
	function delay_download(){
		var length = queue_files_.length;
		if(queue_index_ < length){
			setTimeout(function(){
				alert();
				downer(parseURL(queue_files_[queue_index_]),queue_files_[queue_index_],true);
				queue_index_ = queue_index_ +1;
				delay_download();
			},500);
		}
	};

	return function(files){
		queue_files_ = files;
		queue_index_ = 0;
		downer= h5Down ? downloadFile : IEdownloadFile;
		if(files instanceof Array) {
			delay_download();
		} 
		else if(typeof files === "string") {
			downer(parseURL(files), files);
		} 
		else {
			for(var file in files) downer(file, files[file]);
		}
	};
})();
