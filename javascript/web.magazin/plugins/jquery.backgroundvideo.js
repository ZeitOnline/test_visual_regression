/**
 * @fileOverview jQuery Plugin for Background Video
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */
( function( $ ) {

    /**
     * See (http://jquery.com/).
     * @name jQuery
     * @alias $
     * @class jQuery Library
     * See the jQuery Library  (http://jquery.com/) for full details.  This just
     * documents the function and classes that are added to jQuery by this plug-in.
     */
    /**
     * See (http://jquery.com/)
     * @name fn
     * @class jQuery Library
     * See the jQuery Library  (http://jquery.com/) for full details.  This just
     * documents the function and classes that are added to jQuery by this plug-in.
     * @memberOf jQuery
     */
    /**
     * Controls Background video behaviour
     * @class backgroundVideo
     * @memberOf jQuery.fn
     * @return {object} jQuery-Object for chaining
     */
    $.fn.backgroundVideo = function() {

        //change left position of video to center it
        function setVideoPosition( $element ) {

            var video = $element.find( 'video' ),
                positionLeft = ( $element.width() - video.width() ) / 2,
                positionTop = ( $element.height() - video.height() ) / 2;

            video.css({ left: positionLeft + 'px', top: positionTop + 'px' });

            // prevents the video from glitching
            if ( $element.attr( 'data-backgroundvideo' ) ) {
                video.removeAttr( 'poster' );
            }
        }

        //run through data-backgroundvideo elements
        return this.each( function() {

            var $element = $( this ),
                video = $element.find( 'video' );

            //set video position
            setVideoPosition( $element );

            //start video
            $( video ).get( 0 ).play();

            //on video play, hide image and show video
            $( video ).on( 'play', function() {
                $element.find( '.video--fallback' ).fadeOut();
                $( video ).show();
            });

            //reset video position on resize
            $( window ).on( 'resize', function() {
                setVideoPosition( $element );
            });

        });

    };

})( jQuery );
