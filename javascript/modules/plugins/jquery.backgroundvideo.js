/* global console, Modernizr */
(function( $ ){

	/**
	 * manages backgroundvideo integration
	 */
	$.fn.backgroundVideo = function() {

		var el = {
			/**
			 * change left position of video to center ist
			 * @param {Object} $element
			 */
			setVideoPosition: function( $element ){

				var video = $element.find("video");
				video.css({"left": ($element.width() - video.width())/2 + "px"});
				video.css({"top": ($element.height() - video.height())/2 + "px"});

				/* prevents the video from glitching */
				if( $element.attr( "data-backgroundvideo" ) ){
					video.removeAttr( "poster" );
				}
			},

		};

		//run through data-backgroundvideo elements
		$(this).each(function(){

			var $element = $( this );
			var video = $element.find( "video" );

			Modernizr.addTest( "autoplay", function(){
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
