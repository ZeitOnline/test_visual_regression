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
                videoId;
            if ( elem.length ) {
                videoId = elem.data( 'video-id' );
                video.displayVideo( videoId, { elem: elem });
            }
        }
    };
});
