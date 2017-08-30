/**
 * @fileOverview Module for the homepage videoStage
 * @version  0.1
 */
/**
 * Module for the homepage videoStage
 * @module videoStage
 */
define([ 'jquery', 'web.site/video/video' ], function( $, video ) {
    return {
        init: function() {
            var videoArticles = $( '.video-stage-main .video-large' ),
                links, options;
            if ( videoArticles.length > 0 ) {
                links = videoArticles.find( 'a' );
                links.one( 'click', function( event ) {
                    event.preventDefault();
                    var article = $( this ).closest( 'article' ),
                        container = article.find( '.video-large__container' ),
                        elem = article.find( '.video-thumbnail' ),
                        videoId = article.data( 'video-id' ),
                        playerId = article.data( 'video-player-id' );
                    if ( typeof videoId !== 'undefined' ) {
                        article.find( '.video-text-playbutton' ).addClass( 'video-text-playbutton--hidden' );
                        article.find( '.video-large__inner' ).addClass( 'video-large__inner--playing' );
                        article.find( '.video-large-title' ).addClass( 'video-large-title--playing' );
                        container.unwrap();
                        if ( playerId ) {
                            options = {
                                elem: elem,
                                playerData: {
                                    'accountId': '18140073001',
                                    'playerId': playerId,
                                    'embed': 'default'
                                }
                            };
                        } else {
                            options = { elem: elem };
                        }
                        video.displayVideo( videoId, options );
                    }
                });
            }
        }
    };
});
