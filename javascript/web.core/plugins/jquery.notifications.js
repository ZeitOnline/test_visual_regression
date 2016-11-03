(function( $, window ) {
    $.fn.notifications = function () {
       if (window.location.hash.substr(1) == 'registration_success'){
           $('.notification').removeClass('notification--hidden');
       } else {
           $('.notification').remove();
       }
    };
})( jQuery, window );
