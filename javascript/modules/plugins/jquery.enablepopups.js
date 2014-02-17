/* global console, alert */
(function($){

	/**
	 * generate popup 
	 */
	$.fn.enablePopups = function() {

		/**
		 * run through popup links
		 */
		$(this).each(function(){
			$(this).click(function(e) {
				e.preventDefault();
				window.open($(this).attr('href'), '', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height='+$(this).attr('data-height')+',width='+$(this).attr('data-width'));
			});
		});

	};

})(jQuery);
