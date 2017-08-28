( function( vjs ) {
    // pause when clicking on ads
    var registerPlugin = videojs.registerPlugin || videojs.plugin;
    registerPlugin( 'adClickPause', function() {
        var player = this;
        player.on( 'ads-click', function() {
            player.ima3.adsManager.pause();
        });
    });
})( window.videojs );
