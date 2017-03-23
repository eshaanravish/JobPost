$( document ).ready( function() {
  
  get_watched_repos();
  
  // RESET BUTTON
  $("#reset").click(function()
  {
    $( '#result' ).html( "<h2>Click a button</h2>" );
  }); // close reset click handler
  
  
  //CLICK REPO BUTTON
  $("#repo").click(function()
  {
    var html = "";
    $( '#result' ).html( "" );
    $.ajax({
      url:"https://api.github.com/repos/bvasko/Bootstrap-Select-Box",
      dataType: "jsonp",
      success : function( returndata )
      {
        $('#result').html("");
        var date = new Date(returndata.data.updated_at);
    		date.toDateString()
        var month = date.getMonth() + 1
				var day = date.getDate()
				var year = date.getFullYear()
        date_str = month + "/" + day + "/" + year;
        //console.log(returndata);
        html +="<h2>"+ returndata.data.full_name + "</h2>";
        html +="<h4>" + returndata.data.description + "</h4>";
        html +="<p>Last updated: " + date_str + "</p>";
        $('#result').append( html );
      }
    });
    return false;
  }); // close repo click handler
  
  //CLICK WATCHED BUTTON
  $("#watched").click(function()
   {
    get_watched_repos()
    return false;
   });   //close watched click handler
  

function get_watched_repos() 
{
   
  $( '#result' ).html( "" );
  var html = "<h2>Repos I'm watching</h2>";
  
  $.ajax( {
    	url : "https://api.github.com/users/bvasko/watched",
    	dataType : "jsonp",
    	success : function ( returndata ) {
      	$.each( returndata.data, function ( i, item ) {
        	html += '<li>' +
          	'<h3><a href="' + this.html_url + '">' + this.name + '</a></h3>' +
          	'<ul>' +
          	'<li>' + 'Description: ' + this.description + '</li>' +
          	'<li>' + 'Language: ' + this.language + '</li>' +
          	'<li>' + 'Updated: ' + this.updated_at + '</li>' +
          	'<li>' + 'Owner: ' + this.owner.login + '</li>' +
          	'</ul>' +
          	'</li>';
      	} );
      $( '#result' ).append( html );
     } // close success handler
     });
  
}

});