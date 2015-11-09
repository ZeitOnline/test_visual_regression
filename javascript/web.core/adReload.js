/**
 * @fileOverview API for asynchronely reload ads on webpages
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {

    var debug = false,
    interaction = function( event ) {

    },
    message = function( event ) {
        var messageData, sender, message;
        try {
            messageData = JSON.parse( event.originalEvent.data );
        } catch ( e ) {
            return;
        }
        if ( typeof messageData.sender !== 'string' || typeof messageData.message !== 'string' ) {
            console.error('messageData not completely set')
            return;
        }

    };

    return {
        init: function() {
            // add eventlistener
            $( window ).on( 'interaction.z', interaction );
            // listen to window.messages for channel interactions
            $( window ).on( 'message', message );
        }
    };
});
