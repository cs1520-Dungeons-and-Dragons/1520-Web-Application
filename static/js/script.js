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
			data: JSON.stringify(data),
			context: document,
			success: function(data){
				console.log(data);
				//window.location.href = data.redirect;
				//$('html').html(data);
				document.write(data);
			},
			dataType: 'html',
			contentType: 'application/json;charset=UTF-8'
		});
	});
});