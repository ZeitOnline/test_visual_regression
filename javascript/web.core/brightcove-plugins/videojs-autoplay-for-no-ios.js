( function( vjs ) {
    var videojsAutostartForNonIOSPlugin = function() {
        var player = this;
        var iOS = /iPad|iPhone|iPod/.test( navigator.userAgent ) && !window.MSStream;
        if ( !iOS ) {
            player.on( 'ready', function() {
                player.play();
            });
        }
    };
    var registerPlugin = vjs.registerPlugin || vjs.plugin;
    registerPlugin( 'videojsAutostartForNonIOS', videojsAutostartForNonIOSPlugin );
})( window.videojs );
