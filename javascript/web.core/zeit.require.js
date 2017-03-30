var rjs = require( 'requirejs/require' ),
    $ = require( 'jquery' ),
    Velocity = require( 'velocity' ),
    images = require( 'web.core/images' ),
    define = rjs.define,
    requirejs = rjs.requirejs;

// require common jQery plugin
require( 'jquery.inview' );

// expose to global scope, because some (external) scripts depend on this
window.define = define;
window.require = rjs.require;
window.jQuery = window.$ = $;

// define *all* dependencies that external scripts will ever happen to have
define( 'jquery', [], function() {
    return $;
});
define( 'velocity', [], function() {
    return Velocity;
});
define( 'images', [], function() {
    return images;
});
define( 'jquery.inview', [], function() {});

function requireAmd( queue ) {
    for ( var i = 0, l = queue.length; i < l; i++ ) {
        requirejs.apply( window, queue[ i ]);
    }
}

module.exports = requireAmd;
