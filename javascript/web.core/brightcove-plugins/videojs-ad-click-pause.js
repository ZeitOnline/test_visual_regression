(function( vjs ) {
    // pause when clicking on ads
    vjs.plugin('adClickPause', function(){
        var player = this;
        player.on('ads-click',function( evt ){
            player.ima3.adsManager.pause();
        });
    });
}( window.videojs ));
