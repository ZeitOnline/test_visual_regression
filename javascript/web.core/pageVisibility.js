/**
 * @fileOverview Page Visibility Shim
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( window, document ) {
    var property,
        vendorPrefixes = [ 'ms', 'o', 'moz', 'webkit', '' ],
        support = {},
        eventName,
        prefix;

    while (( prefix = vendorPrefixes.pop() ) !== undefined ) {
        property = ( prefix ? prefix + 'H' : 'h' ) + 'idden';
        support.pageVisibility = document[ property ] !== undefined;

        if ( support.pageVisibility ) {
            eventName = prefix + 'visibilitychange';
            break;
        }
    }

    // normalize to and update document hidden property
    function updatePageVisibility() {
        if ( property !== 'hidden' ) {
            document.hidden = support.pageVisibility ? document[ property ] : undefined;
        }
    }

    updatePageVisibility();

    if ( window.addEventListener ) {
        window.addEventListener( eventName, updatePageVisibility, false );
    }

})( window, document );
