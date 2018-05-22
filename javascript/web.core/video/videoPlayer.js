/**
 * @fileOverview Module for loading video player on page load (video single pages and articles)
 * @version  0.1
 * @module videoPlayer
 */
define([ 'jquery', 'web.site/video/video' ], function( $, video ) {
    return {
        init: function() {
            var $videos = $( '.js-videoplayer' ),
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
