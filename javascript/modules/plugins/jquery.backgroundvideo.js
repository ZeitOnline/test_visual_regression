/* global console */

/**
 * @fileOverview jQuery Plugin for Background Video
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */
(function( $ ){
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

		var el = {
			//change left position of video to center it
			setVideoPosition: function( $element ){

				var video = $element.find("video");
				video.css({"left": ($element.width() - video.width())/2 + "px"});
				video.css({"top": ($element.height() - video.height())/2 + "px"});

				// prevents the video from glitching
				if( $element.attr( "data-backgroundvideo" ) ){
					video.removeAttr( "poster" );
				}
			},

		};

		//run through data-backgroundvideo elements
		return this.each( function() {

			var $element = $( this );
			var video = $element.find( "video" );

			// video already playing?
			if( $(video).get(0).currentTime > 0 ) {
				$element.find( ".video--fallback" ).hide();
				$( video ).show();
			}

			//event on video play
			$( video ).on( "play", function() {
				$element.find( ".video--fallback" ).hide();
				$( video ).show();
			});

			//set initial position of video
			$( window ).on( "load", function(){
				el.setVideoPosition( $element );
			});

			//reset video position on resize
			$( window ).on( "resize", function(){
				el.setVideoPosition( $element );
			});

		});

	};

})( jQuery );
