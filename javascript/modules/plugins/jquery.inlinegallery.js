/* global console */

/**
 * @fileOverview  Inline-Gallery preparation and evokation script
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function($) {
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
	 * Prepares the inline gallery and adds some extra features
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
			hideControlOnEnd: false,
            adaptiveHeight: true,
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

			/* add icons to existing gallery buttons */
			$(".bx-next").addClass('icon-pfeil-rechts');
			$(".bx-prev").addClass('icon-pfeil-links');

			$(".figure__media", this).mouseenter(function() {
				$(this).parents('.bx-wrapper').addClass("bx-wrapper-hovered");
			}).mouseleave(function() {
				$(this).parents('.bx-wrapper').removeClass("bx-wrapper-hovered");
			});

			$(this).on("scaling_ready", function(e) {
				slider.redrawSlider();
				/* add hover-class for button display */
				$(".figure__media", this).mouseenter(function() {
					$(this).parents('.bx-wrapper').addClass("bx-wrapper-hovered");
				}).mouseleave(function() {
					$(this).parents('.bx-wrapper').removeClass("bx-wrapper-hovered");
				});
			});
		});
	};
})(jQuery);
