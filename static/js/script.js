var socket;
$(document).ready(function()
{
	socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.on('connect', function(){
		socket.emit('connection', {data: 'I joined!!!!'});
	});
	
	$('#joindm').click(function(){
		console.log("That doesn't work goofball.");
	});
	
	$('#joinp').click(function(){
		console.log("Joining " + $('#roomname').val() + "...");
		socket.emit('joinRoom', {room: $('#roomname')});
	});
});