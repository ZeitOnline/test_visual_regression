<<<<<<< HEAD
/* global console, alert */
(function($) {

/**
 * See (http://jquery.com/)
 * @name fn
 * @class 
 * See the jQuery Library  (http://jquery.com/) for full details.  This just
 * documents the function and classes that are added to jQuery by this plug-in.
 * @memberOf jQuery
 */
(function($) {
	/**
	 * Inline-Gallery preparation and evokation script 
	 *
	 * @class inlinegallery
	 * @memberOf jQuery.fn
	 * @param  {object} defaults	configuration object, overwriting presetted options
	 * @return {object}	jQuery-Object for chaining
	 */
	$.fn.inlinegallery = function( defaults ) {

		var options = $.extend({
			slideSelector: '.figure-full-width',
			easing: 'ease-in-out',
			pagerType: "short",
			nextText: "Zum nächsten Bild",
			prevText: "Zum vorigen Bild",
			infiniteLoop: true,
			hideControlOnEnd: false
		}, defaults);
		
		return this.each(function(){
			var slider = $( this ).bxSlider( options ),
				ffw = $('<a class="bx-overlay-next icon-pfeil-rechts" href="">Ein Bild vor</a>'),
				rwd = $('<a class="bx-overlay-prev icon-pfeil-links" href="">Ein Bild zurück</a>');

			/* additional buttons on image */
			$(this).parent().parent().append(ffw);
			$(this).parent().parent().append(rwd);
			$(ffw).on("click", function(evt){
				evt.preventDefault();
				slider.goToNextSlide();
			});
			$(rwd).on("click", function(evt){
				evt.preventDefault();
				slider.goToPrevSlide();
			});
			/* add hover-class for button display */
			$(this).find("img").hover(function() {
				$(this).parents('.bx-wrapper').toggleClass("bx-wrapper-hovered");
			}, function() {
				$(this).parents('.bx-wrapper').toggleClass("bx-wrapper-hovered");
			});

			/* add icons to existing gallery buttons */
			$(".bx-next").addClass('icon-pfeil-rechts');
			$(".bx-prev").addClass('icon-pfeil-links');
		});
	};
})(jQuery);