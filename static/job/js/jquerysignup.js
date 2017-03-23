$(function() {
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

	$( "#email" ).blur(function() {
		if ($( this ).val() == ""){
			$( this ).closest( ".form-group" ).addClass( "has-error" );
			$( this ).next( "small" ).removeClass("hidden").addClass("text-danger");
			document.getElementById("e1").innerHTML = "Email required";
		}
		else if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(myForm.email.value)) {
			$( "#email" ).next( "small" ).css("display", "none");
			$( this ).closest( ".form-group" ).removeClass("has-warning").addClass( "has-success" );
		}
		else {
			$( this ).closest( ".form-group" ).addClass( "has-warning" );
			$( this ).next( "small" ).removeClass("hidden").addClass("text-warning");
			document.getElementById("e1").innerHTML = "Email invalid";
		}
	});
});

