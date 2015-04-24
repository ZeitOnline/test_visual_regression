/**
 * @fileOverview Module for the homepage videoStage
 * @version  0.1
 */
/**
 * Module for the homepage videoStage
 * @module videoStage
 */
define([ 'jquery', 'video' ], function( $, video ) {
    return {
        init: function() {
            var article = $( '.video-stage-main .video-large' ),
                link = article.find( 'a' ),
                container = article.find( '.video-large__container' ),
                button = article.find( '.video-text-playbutton' ),
                title = article.find( '.video-large-title' ),
                videoId = article.data( 'video-id' ),
                elem = article.find( '.video-thumbnail' );

            if ( typeof videoId !== 'undefined' ) {
                link.one( 'click', function( evt ) {
                    evt.preventDefault();
                    container.unwrap();
                    button.addClass( 'video-text-playbutton--hidden' );
                    title.addClass( 'video-large-title--playing' );
                    video.displayVideo( videoId, { elem: elem });
                });
            }
        }
    };
});
