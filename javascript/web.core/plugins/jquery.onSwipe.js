/**
 * @fileOverview jQuery Plugin for detecting swipe movements
 * @author thomas.puppe@zeit.de
 * @version  0.1


Usage:

$('.my-elem').onSwipe( function() {
    this.remove();
}, {
    'direction': 'left right'
});

 */
( function( $, Modernizr ) {

    $.fn.onSwipe = function( callbackFunction ) {

        var hasTouch = Modernizr.touchevents;

        /*options = $.extend({
            onSlideAfter: function() {
                // add ad-reloading capability
                var prefix = Zeit.view.ressort === 'zeit-magazin' ? 'zmo-' : '';
                $( window ).trigger( 'interaction.adreload.z', [ prefix + 'gallery', 'interaction' ]);
            },
            slideSelector: '.slide'
        }, settings )*/

        // via http://www.javascriptkit.com/javatutors/touchevents2.shtml
        function swipedetect( el, callback ) {

            var touchsurface = el,
                swipedir,
                startX,
                startY,
                distX,
                distY,
                threshold = 50, //required min distance traveled to be considered swipe
                restraint = 40, // maximum distance allowed at the same time in perpendicular direction
                allowedTime = 500, // maximum time allowed to travel that distance
                elapsedTime,
                startTime,
                handleswipe = callback || function() {};

            touchsurface.addEventListener( 'touchstart', function( e ) {
                var touchobj = e.changedTouches[ 0 ];
                swipedir = 'none';
                startX = touchobj.pageX;
                startY = touchobj.pageY;
                startTime = new Date().getTime(); // record time when finger first makes contact with surface
                //e.preventDefault(); // do not prevent, to enable touch/click on the link (use case: appUserIsBack)
            }, false );

            touchsurface.addEventListener( 'touchmove', function( e ) {
                e.preventDefault(); // prevent scrolling when inside DIV
            }, false );

            touchsurface.addEventListener( 'touchend', function( e ) {
                var touchobj = e.changedTouches[ 0 ];
                distX = touchobj.pageX - startX; // get horizontal dist traveled by finger while in contact with surface
                distY = touchobj.pageY - startY; // get vertical dist traveled by finger while in contact with surface
                elapsedTime = new Date().getTime() - startTime; // get time elapsed
                if ( elapsedTime <= allowedTime ) { // first condition for awipe met
                    if ( Math.abs( distX ) >= threshold && Math.abs( distY ) <= restraint ) {
                        // 2nd condition for horizontal swipe met
                        swipedir = ( distX < 0 ) ? 'left' : 'right'; // if dist traveled is negative, it indicates left swipe
                    } else if ( Math.abs( distY ) >= threshold && Math.abs( distX ) <= restraint ) {
                        // 2nd condition for vertical swipe met
                        swipedir = ( distY < 0 ) ? 'up' : 'down'; // if dist traveled is negative, it indicates up swipe
                    }
                }
                handleswipe( el, swipedir );
                //e.preventDefault(); // do not prevent, to enable touch/click on the link (use case: appUserIsBack)
            }, false );
        }

        return this.each( function() {

            if ( !hasTouch ) {
                return;
            }

            swipedetect( this, callbackFunction );

        });
    };
})( jQuery, window.Modernizr );

/* //////////////////////////

//USAGE:
var el = document.getElementById('someel')
swipedetect(el, function(swipedir){
    swipedir contains either "none", "left", "right", "top", or "down"
    if (swipedir =='left')
        alert('You just swiped left!')
})
*/
