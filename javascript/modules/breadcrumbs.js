/* global console, define, alert */
define(['jquery'], function() {

	/**
	 * show breadcrumbs
	 */
	var init = function() {
		if (window.innerWidth >= 768) {
			var trigger_alternate_caption;
			$(document.getElementById('js-breadcrumbs__trigger')).click(function() {
				trigger_alternate_caption = $(this).data('alternate');
				$(this).data('alternate', $(this).html());
				$(this).html(trigger_alternate_caption);
				$(document.getElementById('js-breadcrumbs')).toggleClass('is-active');
			});
		}
	};

	return {
		init: init
	};

});