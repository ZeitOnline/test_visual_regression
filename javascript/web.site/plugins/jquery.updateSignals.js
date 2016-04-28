/**
 * @fileOverview jQuery Plugin for updating and animated text chunks
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, window, document ) {

    var options = {
            inEffect: { opacity: 0 },
            inVelocity: 500,
            outEffect: { opacity: 1 },
            outVelocity: 500,
            uniqueId: $( document.body ).data( 'uniqueId' ),
            timeEndpoint: '/json/delta_time?unique_id=',
            commentsEndpoint: '/json/comment_count?unique_id='
        };

    /**
     * recursive polling function
     * works with comet(ish) server too, I'd say
     * polls JSON endpoint
     * @param {string} endpoint URL to JSON endpoint
     * @param {Number} interval time in ms between polls
     * @param {string} selector to element which is triggered for update
     * @fires signals.update
     */
    function poll( endpoint, interval, selector ) {

        // If there are no elements on the page, do not poll. This is
        // important for framebuilder-pages, and might be useful on our CPs.
        if ( $( selector ).length === 0 ) {
            return;
        }

        setTimeout(function() {
            // Use page visibility API to skip request if page is hidden
            if ( document.hidden ) {
                poll( endpoint, interval, selector );
            } else {
                $.ajax({
                    url: endpoint + options.uniqueId,
                    dataType: 'json',
                    /**
                     * on successful request emit events
                     * @param {object} data the objectified json pulled from endpoint
                     * @fires signals.update
                     */
                    success: function( data ) {
                        for ( var key in data ) {
                            if ( data.hasOwnProperty( key ) ) {
                                for ( var id in data[ key ] ) {
                                    if ( data[ key ].hasOwnProperty( id ) ) {
                                        $( '[data-unique-id="' + id + '"]' )
                                            .find( selector )
                                            .trigger( 'signals.update', data[ key ][ id ] );
                                    }
                                }
                            }
                        }
                    },
                    /**
                     * on completion go recursive
                     */
                    complete: function() {
                        poll( endpoint, interval, selector );
                    }
                });
            }
        }, interval );
    }

    /**
     * takes new text to animate
     * @param  {object} event the normalized jQuery event object
     * @param  {string} text text to change
     */
    function textAnimation( event, text ) {
        var $elem = $( this );

        if ( $elem.text() !== text ) {
            $elem.velocity( options.inEffect, options.inVelocity, function() {
                $elem
                    .html( text )
                    .delay( 10 )
                    .velocity( options.outEffect, options.outVelocity );
            });
        }
    }

    $.extend({
        /**
         * Polls JSON Endpoint for text updates, and animates them into the dom
         * @memberOf jQuery
         * @category Function
         */
        updateSignals: function() {
            poll( options.timeEndpoint, 1000 * 60, '.js-update-datetime' );
            poll( options.commentsEndpoint, 1000 * 20, '.js-update-commentcount' );

            /**
             * bind event on diverse elements
             * @event  signals.update
             */
            $( '.js-update-datetime, .js-update-commentcount' ).on( 'signals.update', textAnimation );
        }
    });

})( jQuery, window, document );
