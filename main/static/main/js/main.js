

//to load form modal
//<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#add-task-modal">
//	Add a Task
//</button>


var dpi = {};

dpi.attachFormModalEvents = function() {
    $('.ajax-form').submit(function(e) {
        e.preventDefault();
        $('.ajax-form-button').attr("disabled", true);
        var url = $(this).attr('data-url');
        //var data = $(this).serialize();
        var formData = new FormData(this);  //needed to handle file uploads
        $.ajax({
            url: url,
            type: "POST",
            data: formData,
            processData: false,		// needed to handle file uploads
        	contentType: false,		// needed to handle file uploads
        })
        .done(function( json ) {
            if (json.status == 'complete') {
                // this line prevents a reload of a POST request
                window.location = window.location.href;
                location.reload();
            } else {
                $('#generic-form-modal-title').html(json.title);
                $('#generic-form-modal-body').html(json.html);
                dpi.attachFormModalEvents();
            }
        })
        .fail(function( xhr, status, errorThrown ) {
            alert( "error" );
            console.log( "Error: " + errorThrown );
            console.log( "Status: " + status );
            console.dir( xhr );
        });
    });
}

$(document).ready(function() {

    $('[data-toggle="popover"]').popover();

    
    $('.open-form-modal').click(function() {
        var url = $(this).attr('data-url');
        $('#generic-form-modal-title').html('Loading...');
        $('#generic-form-modal-body').html('');
        $('#generic-form-modal').modal('show');
        $.ajax({
            url: url,
            type: "GET",
            dataType : "json",
        })
        .done(function( json ) {
            $('#generic-form-modal-title').html(json.title);
            $('#generic-form-modal-body').html(json.html);
            dpi.attachFormModalEvents();
        })
        .fail(function( xhr, status, errorThrown ) {
            alert( "error" );
            console.log( "Error: " + errorThrown );
            console.log( "Status: " + status );
            console.dir( xhr );
        });
    });
    
    
    
});