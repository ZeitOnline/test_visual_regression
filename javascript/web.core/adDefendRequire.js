/**
 * @fileOverview Module adDefend
 * @version  0.1
 */

/**
 * adDefendRequire.js init adDefend
 * @function init
 */
function init() {

    if ( !document.querySelector( '#addefend-overlay' ) ) {

        /**
         * require adDefend
         */
        require([ 'web.core/adDefend' ], function( adDefend ) {
            adDefend();
        });
    }
}

module.exports = {
    init: init
};
