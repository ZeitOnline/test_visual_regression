/**
 * @fileOverview API for asynchronely reload ads on webpages
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {

    var debug = false,
    /**
     * initialize a new counting mandator by checking id against configuration
     * @return {bool}   return state when ready
     */
    initialize = function() {
        console.debug( 'initialize' );
        // ggf. config laden
        // im localstorage ablegen
        // returnen
    },
    interaction = function( event, sender, message ) {
        console.debug( 'interaction', event, sender, message );
        // check config
        // check session storage
        // defer_counting
    },
    /**
     * channel filtered window.messages to interaction api
     * @param  {object} event DOM event
     * @return {void}
     */
    message = function( event ) {
        var messageData, sender, message;
        try {
            messageData = JSON.parse( event.originalEvent.data );
        } catch ( e ) {
            return;
        }
        if ( typeof messageData.sender !== 'string' || typeof messageData.message !== 'string' ) {
            console.error( 'messageData not completely set' );
            return;
        }
        $( window ).trigger( 'interaction.adreload.z', [ sender, message ]);
    };

    return {
        init: function() {
            // configure page
            if ( initialize() ) {
                // add eventlistener
                $( window ).on( 'interaction.adreload.z', interaction );
                // listen to window.messages for channel interactions
                $( window ).on( 'message', message );
            }
            // on page unload unbind all at unload to prevent memory leaks
            $( window ).on( 'unload', function( event ) {
                $( window ).off( 'adreload' );
            });
        }
    };
});
