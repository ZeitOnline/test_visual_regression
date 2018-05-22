/**
 * @fileOverview Module for the video single pages
 * @version  0.1
 */
/**
 * Module for the video single pages
 * @module videoSinglepage
 */
define([ 'jquery', 'web.site/video/video' ], function( $, video ) {
    return {
        init: function() {
            var elem = $( '.js-videosinglepage' ),
                videoId,
                videoAdvertising,
                videoPlayertype;
            if ( elem.length ) {
                videoId = elem.data( 'video-id' );
                videoAdvertising = elem.data( 'video-advertising' );
                videoPlayertype = elem.data( 'video-playertype' );

                video.displayVideo( videoId, {
                    elem: elem,
                    advertising: videoAdvertising,
                    playertype: videoPlayertype
                });
            }
        }
    };
});
