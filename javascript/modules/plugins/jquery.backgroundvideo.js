/* global console, alert, Modernizr */
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

				$.each( video.find( "source" ), function( index, value ){
					console.debug( value );
				});
				
				/* prevents the video from glitching */
				if( $element.attr('data-backgroundvideo') ){
					video.removeAttr("poster");
				}
			},
			/**
			 *
			 * @param  {string} src_url [url of src to test]
			 * @return {[type]}         [description]
			 */
			srcExists: function(src_url){
				var http = new XMLHttpRequest();
				http.open('HEAD', src_url, false);
				http.send();
				return http.status !== 404;
			}
		};

		//run through data-backgroundvideo elements
		$(this).each(function(){
			var $element = $( this );
			
			//show image instead of video when on mobile or no html5 video avaiable
			if( Modernizr.touch || !Modernizr.video ) {

				$element.find( "video" ).remove();
				$element.find( ".video--fallback" ).show();

			}else{
				
				//set initial position of video
				el.setVideoPosition( $element );

				//reset video position on resize
				$( window ).on("resize", function(){
					el.setVideoPosition( $element );
				});

			}
			
		});

	};

})( jQuery );