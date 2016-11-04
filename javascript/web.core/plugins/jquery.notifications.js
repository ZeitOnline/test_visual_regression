(function( $, window ) {
    $.fn.notifications = function () {
       if (window.location.hash.substr(1) == 'registration_success'){
           $('.notification--registration').removeClass('notification--hidden');
       } else {
           $('.notification--registration').remove();
       }
    };
})( jQuery, window );
