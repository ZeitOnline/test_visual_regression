/**
 * @fileOverview jQuery Plugin for calling the Sharebert feature on
 * article blocks.
 * @author thomas.puppe@zeit.de
 * @version 0.1
 */
( function( $, Zeit ) {

    'use strict';

    var settings,
        defaults = {
            duration: 200
        };

    function log( message ) {
        window.console.log( message );
    }

    function initShareBlocks( element ) {
        log( 'initialize' + element );
    }

    $.fn.shareBlocks = function( options ) {
        settings = $.extend({}, defaults, options );

        log( 'setup with ' + Zeit + ' and ' + settings );

        return this.each( function() {
            initShareBlocks( this );
        });
    };
})( jQuery, window.Zeit );
