/* global console */
(function( $ ){

	/**
	 * manages esiparsing if there's no varnish
	 */
	$.fn.parseEsi = function() {

		$( this ).each( function(){
			window.do_esi_parsing( document );
		});

	};

})( jQuery );
