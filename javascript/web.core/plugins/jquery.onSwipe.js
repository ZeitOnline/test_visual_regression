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
                threshold = 100, // required min distance traveled to be considered swipe
                restraint = 40, // maximum distance allowed at the same time in perpendicular direction
                handleswipe = callback || function() {};

            touchsurface.addEventListener( 'touchstart', function( e ) {
                var touchobj = e.changedTouches[ 0 ];
                swipedir = 'none';
                startX = touchobj.pageX;
                startY = touchobj.pageY;
                touchsurface.style.transition = 'unset';
                //e.preventDefault(); // do not prevent, to enable touch/click on the link (use case: appUserIsBack)
            }, false );

            touchsurface.addEventListener( 'touchmove', function( e ) {
                e.preventDefault(); // prevent scrolling when inside DIV
                var touchobj = e.changedTouches[ 0 ];
                var movementX = touchobj.pageX - startX;
                // TODO add handling for vertical movement
                touchsurface.style.transform = 'translateX(' + movementX + 'px)';
            }, false );

            touchsurface.addEventListener( 'touchend', function( e ) {
                var touchobj = e.changedTouches[ 0 ];
                distX = touchobj.pageX - startX; // get horizontal dist traveled by finger while in contact with surface
                distY = touchobj.pageY - startY; // get vertical dist traveled by finger while in contact with surface
                if ( Math.abs( distX ) >= threshold && Math.abs( distY ) <= restraint ) {
                    // 2nd condition for horizontal swipe met
                    swipedir = ( distX < 0 ) ? 'left' : 'right'; // if dist traveled is negative, it indicates left swipe
                } else if ( Math.abs( distY ) >= threshold && Math.abs( distX ) <= restraint ) {
                    // 2nd condition for vertical swipe met
                    swipedir = ( distY < 0 ) ? 'up' : 'down'; // if dist traveled is negative, it indicates up swipe
                } else {
                    // Swipe distance was too short, bounce element back to origin
                    // TODO add handling for vertical movement
                    touchsurface.style.transition = 'transform 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                    touchsurface.style.transform = 'translateX(0px)';
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
