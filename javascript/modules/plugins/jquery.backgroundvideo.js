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

			//set video position
			el.setVideoPosition( $element );

			//start video
			if ( Modernizr.video ) {
				$(video).get(0).play();
			}

			//on video play, hide image and show video
			$( video ).on( "play", function() {
				$element.find( ".video--fallback" ).fadeOut();
				$( video ).show();
			});

			//reset video position on resize
			$( window ).on( "resize", function(){
				el.setVideoPosition( $element );
			});

		});

	};

})( jQuery );
