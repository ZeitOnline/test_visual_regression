(function( vjs ) {

    var webtrekkPlugin = function( options ) {
        var player = this,
        sendEventToWebtrekk = function( trekkString ) {
            var messageData = {
                'sender': 'videojsWebtrekk',
                'message': trekkString
            };
            window.parent.postMessage( JSON.stringify( messageData ), '*' );
        };

        // the play event is triggered on several occasions:
        // - two(!) times on start (with currentTime undefined and currentTime 0)
        // - on resume (after pause).
        // - on jumping to another position in the video
        // That's why we ose one() for registering the event. (Another solution
        // would be to check for that one event which has currentTime===0.)
        player.one( 'play', function( e ) {
            sendEventToWebtrekk( 'play' );
        });

        // contentplayback is triggered when the real video content begins.
        // It does not matter if an ad was played before or not.
        // But: it is triggered again at the end of a video. Hence, "one()".
        player.one( 'contentplayback', function( e ) {
            sendEventToWebtrekk( 'start' );
        });

        // one() just to be sure (see above)
        player.one( 'ended', function( e ) {
            sendEventToWebtrekk( 'complete' );
        });

        // -------------------------------------------------------------------------
        if ( options.debugMode === true ) {

            window.console.log( '1508: Starte Plugin mit Debug-Modus ' + options.debugMode );

            player.on( 'play', function( e ) {
                window.console.groupCollapsed( 'DEBUG: PLAY' );
                window.console.log( e );
                window.console.log( this );
                window.console.groupEnd();
            });
        }

        /*
        Events: http://docs.brightcove.com/en/video-cloud/brightcove-player/reference/api/vjs.Player.html#eventsSection
        Interessante Properties:
        - this.techName (Html5 - vermutlich vs Flash)
        - this.options.autoplay
        */

    };

    vjs.plugin( 'webtrekk', webtrekkPlugin );

}( window.videojs ));
