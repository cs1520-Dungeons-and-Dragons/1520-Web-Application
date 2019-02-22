$(document).ready(function()
{
	$('#joindm').click(function(){
		console.log("That doesn't work goofball.");
	});
	/*
	$('#joinp').click(function(){
		let data = {user: $('#user').val(), room: $('#roomname').val()};
		var jqxhr = $.ajax({
			type: "POST",
			url: '/joinRoom',
			data: JSON.stringify(data),
			statusCode: {
				278: function(response) {
					console.log("redirect");
					window.location.href = response.location;
				},
				200: function(response) {
					document.write(response);
				}
			},
			contentType: 'application/json;charset=UTF-8'
		});
	});*/
});