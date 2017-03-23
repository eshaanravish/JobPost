$( "input" ).blur(function() {
if ( $(this).parent().hasClass("bootstrap-tagsinput") ) {
	if ($("#interests").val() == ""){
		$("#interests").closest( ".form-group" ).addClass( "has-error" );
		$("#interests").next( "small" ).removeClass("hidden").addClass("text-danger");
	}
	else {
		$("#interests").closest( ".form-group" ).removeClass( "has-error" ).addClass("has-success");
		$("#interests").next( "small" ).addClass("hidden").removeClass("text-danger");
	}
} else {
	if ($( this ).val() == ""){
		$( this ).closest( ".form-group" ).addClass( "has-error" );
		$( this ).next( "small" ).removeClass("hidden").addClass("text-danger");
	}
	else {
		$( this ).closest( ".form-group" ).removeClass( "has-error" ).addClass("has-success");
		$( this ).next( "small" ).addClass("hidden").removeClass("text-danger");
	}
}
});

