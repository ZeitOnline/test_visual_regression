/**
 * @fileOverview jQuery Plugin for updating and animated text chunks
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $ ) {
    /**
    * See (http://jquery.com/)
    * @name jQuery
    * @alias $
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    */
    /**
    * See (http://jquery.com/)
    * @name fn
    * @class jQuery Library
    * See the jQuery Library  (http://jquery.com/) for full details.  This just
    * documents the function and classes that are added to jQuery by this plug-in.
    * @memberOf jQuery
    */
    /**
    * Polls JSON Endpoint for text updates, and animates the into the dom
    * @class up2dateSignals
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    * @todo remove faked endpoints and count in favor of real data
    */
    $.fn.up2dateSignals = function( options ) {

        var defaults = $.extend({
            inEffect: { opacity: 0 },
            inVelocity: 500,
            outEffect: { opacity: 1 },
            outVelocity: 500,
            uniqueId: $( this ).data('uniqueId'),
            timeEndpoint: '/json/delta_time?unique_id=',
            commentsEndpoint: '/json/comment_count?unique_id='
        }, options),
        // remove this, when the real endpoint is in use
        fakecounter = 1,
        /**
         * recursive polling function
         * works with comet(ish) server too, I'd say
         * polls JSON endpoint
         * @param {string} endpoint URL to JSON endpoint
         * @param {Number} interval time in ms between polls
         * @param {string} selector to element which is triggered for update
         * @fires singals:update
         * @todo remove fake endpoint and counter
         * @todo put together apis
         * @todo read endpoint param from data-uniqueID of the body (which is also a todo)
         */
        poll = function( endpoint, interval, selector ) {
            setTimeout(function() {
                $.ajax({
                    // replace with real endpoint
                    url: endpoint + defaults.uniqueId,
                    /**
                     * on successful request emit events
                     * @param  {object} data the objectified json pulled from endpoint
                     * @fires   singals:update
                     */
                    success: function( data ) {
                        $.each(data, function(i, name) {
                            $.each(name, function(identifier, object) {
                                // account for differing api
                                if ( typeof object !== 'object') {
                                    $('[data-unique-id=\'' + identifier + '\']')
                                    .find( selector )
                                    .trigger( 'signals.update', object );
                                } else {
                                    for ( var name in object ) {
                                        if (object.hasOwnProperty(name)) {
                                            $('[data-unique-id=\'' + name + '\']')
                                            .find( selector )
                                            .trigger( 'signals.update', object[name].time );
                                        }
                                    }
                                }
                            });
                        });
                        // remove this when real endpoint is in use
                        // not in use? [ms]
                        fakecounter = fakecounter % 6 + 1;
                    }, dataType: 'json',
                    /**
                     * on completion go recursive
                     */
                    complete: function() {
                        poll( endpoint, interval, selector );
                    }
                });
            }, interval);
        },
        /**
         * takes new text to animate
         * @param  {object} event the normalized jQuery event object
         * @param  {string} text text to change
         */
        textAnimation = function( event, text ) {
            var $elem = $( this );

            if ( $elem.text() !== text ) {
                $elem.animate( defaults.inEffect, defaults.inVelocity, function() {
                    $elem
                    .html( text )
                    .delay( 10 )
                    .animate( defaults.outEffect, defaults.outVelocity);
                });
            }
        };

        return this.each( function() {

            poll( defaults.timeEndpoint, 1000 * 60, '.js-update-datetime');
            poll( defaults.commentsEndpoint, 1000 * 20, '.js-update-commentcount');
            /**
             * bind event on diverse elements
             * @event  signals.update
             */
            $( '.js-update-datetime, .js-update-commentcount' ).on('signals.update', textAnimation);

        });
    };
})( jQuery );
