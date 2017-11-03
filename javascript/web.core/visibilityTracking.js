define([ 'web.core/clicktracking' ], function( Clicktracking ) {

    var observer;

    var handleIntersectionEvent = function( targets ) {
        // we only have one element for now, and do not have to iterate over them
        if ( targets[ 0 ].isIntersecting ) {
            Clicktracking.send([ 'article.schranke...view', '#schranke-' + window.Zeit.view.paywall ]);
            observer.disconnect();
            // müssen/können wir jetzt das ganze Modul wegschmeißen?
        }
    };

    var init = function() {
        // Beizeiten schauen, ob der Browser das überhaupt mitmacht.
        // Polyfill?
        observer = new window.IntersectionObserver(
            handleIntersectionEvent,
            { threshold: 0.5 }
        );
        observer.observe( document.querySelector( '.gate' ) );

        // Die API unseres Plugins muss das Observen beliebiger
        // Dinge entgegennhmen. Und diese Targets muss man alle
        // hinzufügen und löschen können. Das kann ein einziger Observer
        // erledigen ... wenn wir die Actions koordiniert kriegen.
    };

    return {
        init: init
    };
});
