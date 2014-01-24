/* global console, define, _this */

define(["jquery"], function($) {

	$.fn.inlinegallery = function( defaults ) {

		var options = $.extend({
			slideSelector: '.figure-full-width',
			easing: 'ease-in-out',
			pagerType: "short",
			nextText: "Zum nächsten Bild",
			prevText: "Zum vorigen Bild",
			infiniteLoop: false,
			hideControlOnEnd: true
		}, defaults);
		
		return this.each(function(){
			var slider = $( this ).bxSlider( options );
			$('.figure__media', slider).on("click", function(){
				slider.goToNextSlide();
			});
			$(".bx-next").addClass('icon-pfeil-hover-rechts');
			$(".bx-prev").addClass('icon-pfeil-hover-links');
		});
	};

});