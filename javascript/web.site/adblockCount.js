// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/**
 * @fileOverview Module for losely counting adblocker user (just trends not excact counts)
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define([ 'jquery' ], function( $ ) {
    return {
        init: function() {
            var track = {
                category: 'adb',
                action: false
            }, container, test1, test2;
            $( window ).on( 'load', function( evt ) {
                if ( $( '#iqadtile3999:hidden' ).length > 0  ) {
                    track.action = true;
                    track.opt_label = 'adblockdesktop';
                }
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push( track );
            });
            // planned feature
            // $( window ).load( function( evt ) {
            //     container = $( '<div>' ).css({
            //         position: 'absolute',
            //         top: '-9999px',
            //         left: '-9999px',
            //         visibilty: 'hidden'
            //     });
            //     container.appendTo( 'body' );
            //     test1 = $( '<div id="fonttest--1">ABC</div>' ).css({
            //         'font-family': 'TabletGothic',
            //         'font-size': '100px',
            //         'display': 'inline'
            //     });
            //     test2 = $( '<div id="fonttest--2">ABC</div>' ).css({
            //         'font-family': 'sans-serif',
            //         'font-size': '100px',
            //         'display': 'inline'
            //     });
            //     test1.appendTo( container );
            //     test2.appendTo( container );
            //     console.debug( 'clone width before: ', test1.width() );
            //     console.debug( 'clone width after: ', test2.width() );
            // });
            // if ( window.navigator.doNotTrack > 0 ) {
            //     track.doNotTrack = true;
            // }
        }
    };
});
