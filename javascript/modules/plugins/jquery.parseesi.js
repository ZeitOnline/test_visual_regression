/**
 * @fileOverview jQuery Plugin to activate esi parser
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
     * Manages esiparsing if there's no varnish
     * @class parseEsi
     * @memberOf jQuery.fn
     */
	$.fn.parseEsi = function() {

		$( this ).each( function(){
			window.do_esi_parsing( document );
		});

	};

})( jQuery );
