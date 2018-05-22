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
            var $videos = $( '.js-videosinglepage' ),
                videoId,
                videoAdvertising,
                videoPlayertype;

            $videos.each( function() {
                var $video = $( this );

                videoId = $video.data( 'video-id' );
                videoAdvertising = $video.data( 'video-advertising' );
                videoPlayertype = $video.data( 'video-playertype' );

                video.displayVideo( videoId, {
                    elem: $video,
                    advertising: videoAdvertising,
                    playertype: videoPlayertype
                });
            });
        }
    };
});
