/**
 * @fileOverview Module WMTicker
 * @version  0.1
 */

/**
 * wmTickerRequire.js init wmTicker
 * @function init
 */
function init() {
    var elements = document.getElementsByClassName( 'wm-ticker' );

    if ( elements.length === 1 ) {

        /**
         * require wmTicker library
         */
        require([ 'web.site/wmTicker' ], function( wmTicker ) {
            wmTicker( elements[ 0 ]);
        });
    }
}


module.exports = {
    init: init
};
