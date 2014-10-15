/* global console */

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
    * @requires blast.js
    * @return {object} jQuery-Object for chaining
    * @todo remove faked endpoints and count in favor of real data
    *
    */
    $.fn.up2dateSignals = function( options ) {

        var defaults = $.extend({
            pollingTime: 30 * 1000, // 30 sec.
            inEffect: { opacity: 0 },
            inVelocity: 500,
            outEffect: { opacity: 1 },
            outVelocity: 500
        }, options),
        // remove this, when the real endpoint is in use
        fakecounter = 1,
        // recursive long polling function
        // works with comet server too, I'd say
        // polls the json endpoint and triggers the animation
        poll = function() {
            setTimeout(function() {
                $.ajax({
                    // replace with real endpoint
                    url: '/js/static/fakeJsonEndpoint/endpoint-' + fakecounter + '.json',
                    success: function( data ) {
                        $.each(data.feed[0], function(name, object) {
                            // update dates
                            $('[data-uniqueId=\'' + name + '\']')
                            .find( '.teaser__datetime' )
                            .trigger( 'signals:update', object.time );
                            // update comments
                            $('[data-uniqueId=\'' + name + '\']')
                            .find( '.teaser__commentcount' )
                            .trigger( 'signals:update', object.comments );
                        });
                        // remove this when real endpoint is in use
                        fakecounter = fakecounter < 6 ? fakecounter + 1 : 1;
                    }, dataType: 'json',
                    complete: function() {
                        poll();
                    }
                });
            }, defaults.pollingTime);
        },
        textAnimation = function( elem, text ) {
            text = text || elem.text();
            var textArr = text.split(' '),
            elems = elem.blast({
                delimiter: 'word',
                aria: true,
                generateValueClass: true
            }),
            elemsToAnimate = [];
            elems.each( function( i, n ) {
                if ( $(n).text() !== textArr[i] ) {
                    elemsToAnimate.push( i );
                }
            });
            elems.each( function( i, n ) {
                if ( $.inArray(i, elemsToAnimate) > -1 ) {
                    $(n).animate( defaults.inEffect, defaults.inVelocity, function() {
                        $(this)
                        .html( textArr[i] )
                        .delay( 10 )
                        .animate( defaults.outEffect, defaults.outVelocity);
                    });
                }
            });
        };

        return this.each( function() {

            poll();

            $( '.teaser__datetime, .teaser__commentcount' ).bind('signals:update', function( event, data ) {
                textAnimation( $(event.target), data );
            });

        });
    };
})( jQuery );
