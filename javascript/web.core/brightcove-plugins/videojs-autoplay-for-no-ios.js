(function( vjs ) {
    var videojsAutostartForNonIOSPlugin = function( options ) {
        var player = this;
        var iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if(!iOS) {
            player.on('ready', function(){
                player.play();
            });
        }
    };
    vjs.plugin( 'videojsAutostartForNonIOS', videojsAutostartForNonIOSPlugin );
}( window.videojs ));
