/* global console */

/**
 * @fileOverview jQuery Plugin for Popups
 * @version  0.1
 */
(function($){
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
     * Enables Pop-ups
     * @class enablePopups
     * @memberOf jQuery.fn
     * @return {object} jQuery-Object for chaining
     */
	$.fn.enablePopups = function() {

		//run through popup links
		return this.each( function() {
			$(this).click(function(e) {
				e.preventDefault();
				window.open($(this).attr('href'), '', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height='+$(this).attr('data-height')+',width='+$(this).attr('data-width'));
			});
		});

	};

})(jQuery);
