(function( vjs ) {

    var videojsEventBroadcastPlugin = function( options ) {
        var player = this,
        postEventToWindow = function( eventString ) {
            var messageData = {
                'name': 'zonTriggeredEventTracking',
                'sender': 'videojs',
                'event': eventString
            };
            window.parent.postMessage( JSON.stringify( messageData ), '*' );
        };

        // the play event is triggered on several occasions:
        // - two(!) times on start (with currentTime undefined and currentTime 0)
        // - on resume (after pause).
        // - on jumping to another position in the video
        // That's why we choose one() for registering the event. (Another solution
        // would be to check for that one event which has currentTime===0.)
        player.one( 'play', function( e ) {
            postEventToWindow( 'playerStarted' );
        });

        // contentplayback is triggered when the real video content begins.
        // It does not matter if an ad was played before or not.
        // But: it is triggered again at the end of a video. Hence, "one()".
        player.one( 'contentplayback', function( e ) {
            postEventToWindow( 'contentStarted' );
        });

        // one() just to be sure (see above)
        player.one( 'ended', function( e ) {
            postEventToWindow( 'contentCompleted' );
        });

        /*
        Events: http://docs.brightcove.com/en/video-cloud/brightcove-player/reference/api/vjs.Player.html#eventsSection
        Interessante Properties:
        - this.techName (Html5 - vermutlich vs Flash)
        - this.options.autoplay
        */

    };

    vjs.plugin( 'videojsEventBroadcast', videojsEventBroadcastPlugin );

}( window.videojs ));
