var socket;
console.log("before doc");
$(document).ready(function(){
    console.log("doc loaded");
	socket = io.connect('http://' + document.domain + ':' + location.port + '/play');
	socket.on('connect', function(){
		socket.emit('joined', {});
	});
	
	socket.on('status', function(data){
		$('#chatlog').val($('#chatlog').val() + '<' + data.msg + '>\n');
		$('#chatlog').scrollTop($('#chatlog')[0].scrollHeight);
	});
	
	socket.on('message', function(data){
		$('#chatlog').val($('#chatlog').val() + data.msg + '\n');
		$('#chatlog').scrollTop($('#chatlog')[0].scrollHeight);
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
function leave_room(){
    socket.emit('left', {}, function(){
        socket.disconnect();
        window.location.href = "/static/index.html";
    });
}