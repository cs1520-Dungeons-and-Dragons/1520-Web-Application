var socket;
$(document).ready(function(){
	socket = io.connect('http://' + document.domain + ':' + location.port + '/play');
	socket.on('connect', function(){
		socket.emit('joined', {});
	});
	
	socket.on('status', function(data){
		$('#chatlog').val($('#chat').val() + '<' + data.msg + '>\n');
		$('#chatlog').scrollTop($('#chat')[0].scrollHeight);
	});
	
	socket.on('message', function(data){
		$('#chatlog').val($('#chat').val() + data.msg + '\n');
		$('#chatlog').scrollTop($('#chat')[0].scrollHeight);
	});
	
	$('#text').keypress(function(e){
		var code = e.keyCode || e.which;
		if(code == 13)
		{
			text = $('#text').val();
			$('#text').val('');
			socket.emit('text', {msg: text});
		}
	});
});