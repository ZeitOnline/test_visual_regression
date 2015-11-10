/**
 * @fileOverview API for asynchronely reload ads on webpages
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {

    var debug = false,
    configUrl = window.ZMO.jsconfHost + '/config_adreload.json',
    config = true,
    /**
     * initialize a new counting mandator by checking id against configuration
     * @return {bool}   return state when ready
     */
    initialize = function() {
        console.debug( 'initialize' );
        var $deferred = $.Deferred();
        // ggf. config laden
        if ( config === false ) {
            console.debug( 'ajax routine' );
            return $.ajax( configUrl, { dataType: 'json' });
        } else {
            $deferred.resolve();
        }
        // im localstorage ablegen
        // returnen
        return $deferred.promise();
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
            console.debug( 'init' );
            // configure page
            var promise = initialize();
            promise.done( function() {
                config = promise.responseJSON;
                // add eventlistener
                $( window ).on( 'interaction.adreload.z', interaction );
                // listen to window.messages for channel interactions
                $( window ).on( 'message', message );
            });
            // on page unload unbind all at unload to prevent memory leaks
            $( window ).on( 'unload', function( event ) {
                $( window ).off( 'adreload' );
            });
        }
    };
});
