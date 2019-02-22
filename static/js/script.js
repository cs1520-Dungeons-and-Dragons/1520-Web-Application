$(document).ready(function()
{
	$('#joindm').click(function(){
		console.log("That doesn't work goofball.");
	});
	
	$('#joinp').click(function(){
		let data = {user: $('#user').val(), room: $('#roomname').val()};
		var jqxhr = $.ajax({
			type: "POST",
			url: '/joinRoom',
			data: data,
			success: function(data){console.log("request sent.");},
			dataType: "text"
		});
	});
});