( function( vjs ) {

    /*
     * This file is stored in vivi (http://vivi.zeit.de/repository/static/js/brightcove-plugins/)
     * and included into the players via http://scripts.zeit.de/static/js/brightcove-plugins/videojs-event-broadcast.js .
     * But we keep a copy inside the repository to have it greppable and to keep a file history.
     *
     */
    var videojsEventBroadcastPlugin = function() {
        var player = this;

        function postEventToWindow( eventString ) {
            var messageData = {
                'name': 'zonTriggeredEventTracking',
                'sender': 'videojs',
                'event': eventString
            };
            window.parent.postMessage( JSON.stringify( messageData ), '*' );
        }

        // the play event is triggered on several occasions:
        // - two(!) times on start (with currentTime undefined and currentTime 0)
        // - on resume (after pause).
        // - on jumping to another position in the video
        // That's why we choose one() for registering the event. (Another solution
        // would be to check for that one event which has currentTime===0.)
        player.one( 'play', function() {
            postEventToWindow( 'playerStarted' );
        });

        // contentplayback is triggered when the real video content begins.
        // It does not matter if an ad was played before or not.
        // But: it is triggered again at the end of a video. Hence, "one()".
        player.one( 'contentplayback', function() {
            postEventToWindow( 'contentStarted' );
        });

        // one() just to be sure (see above)
        player.one( 'ended', function() {
            postEventToWindow( 'contentCompleted' );
        });

        player.on( 'ads-ad-started', function() {
            postEventToWindow( 'adStarted' );
        });

        /*
        Events: http://docs.brightcove.com/en/video-cloud/brightcove-player/reference/api/vjs.Player.html#eventsSection
        Interessante Properties:
        - this.techName (Html5 - vermutlich vs Flash)
        - this.options.autoplay
        */

    };
    var registerPlugin = vjs.registerPlugin || vjs.plugin;
    registerPlugin( 'videojsEventBroadcast', videojsEventBroadcastPlugin );

})( window.videojs );
