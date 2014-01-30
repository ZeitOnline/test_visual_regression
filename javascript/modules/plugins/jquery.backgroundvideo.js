/* global console, alert, Modernizr */


(function( $ ){

	$.fn.backgroundVideo = function() {

		var el = {
			setVideoPosition: function( $element ){
				var video = $element.find("video");
				video.css({"left": ($element.width() - video.width())/2 + "px"});
			}
		};

		//run through data-backgroundvideo elements
		$(this).each(function(){
			
			var $element = $( this );
	
			if( Modernizr.touch || !Modernizr.video ) {

				$element.find( "video" ).remove();
				$element.find( "div" ).show();

			}else{
				
				el.setVideoPosition( $element );

				//reset video position on resize
				$( window ).on("resize", function(){
					el.setVideoPosition( $element );
				});

			}
			
		});

	};

})( jQuery );