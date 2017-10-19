/**
 * @fileOverview Store GET parameter values in Cookies. So far, only used for DPV icode.
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
define([ 'web.core/zeit' ], function( Zeit ) {

    // utility function might be moved somewhere else if we need it in more than one place
    function findGetParameter( parameterName ) {
        var result = null,
            tmp = [];
        var items = location.search.substr( 1 ).split( '&' );
        for ( var index = 0; index < items.length; index++ ) {
            tmp = items[ index ].split( '=' );
            if ( tmp[ 0 ] === parameterName ) {
                result = decodeURIComponent( tmp[ 1 ]);
            }
        }
        return result;
    }

    return {
        init: function() {

            window.addEventListener( 'load', function() {
                // param sent by DPV, stored in cookie, and consumed by premium.zeit.de
                var icodeValue = findGetParameter( 'wt_cc1' );
                if ( icodeValue ) {
                    Zeit.cookieCreate( 'icode', icodeValue, 365, 'zeit.de' );
                }
            });

        }
    };
});
