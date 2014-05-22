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
            adaptiveHeight: true
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

			$(".scaled-image", this).mouseenter(function() {
				$(this).parents('.bx-wrapper').addClass("bx-wrapper-hovered");
			}).mouseleave(function() {
				$(this).parents('.bx-wrapper').removeClass("bx-wrapper-hovered");
			});

			$(this).on("scaling_ready", function(e) {
				slider.redrawSlider();
                figInMediaRes();
                figCaptionSizing( $(e.target) );
				/* add hover-class for button display */
				$(".scaled-image", this).mouseenter(function() {
					$(this).parents('.bx-wrapper').addClass("bx-wrapper-hovered");
				}).mouseleave(function() {
					$(this).parents('.bx-wrapper').removeClass("bx-wrapper-hovered");
				});
			});

            var mqMobile = window.matchMedia( "(max-width: 576px)" );
            var figures = $('.gallery .inline-gallery .figure-full-width');

            var originalCaptionTexts = [];
            figures.each(function( index ) {
                originalCaptionTexts.push($( this ).find('.figure__caption__text').text());
            });

            function addPagerToCaption(){
                figures.each(function( index ) {
                    var captionText = $( this ).find('.figure__caption__text').text();
                    $( this ).find('.figure__caption__text').html(index + '/' + (figures.length-2) + " " + captionText );
                });
            }

            function removePagerFromCaption(){
                figures.each(function( index ) {
                    $( this ).find('.figure__caption__text').html( originalCaptionTexts[index] );
                });
            }

            if (mqMobile.matches) {
                addPagerToCaption();
                figures.on("click", function(){
                    figures.find('.figure__caption').toggle();
                    $('.bx-overlay-next, .bx-overlay-prev').toggle();
                });
            }

            mqMobile.addListener(function(){
                if (mqMobile.matches) {
                    addPagerToCaption();
                    $('.bx-overlay-next, .bx-overlay-prev').hide();
                    figures.find('.figure__caption').hide();
                    figures.on("click", function(){
                        figures.find('.figure__caption').toggle();
                        $('.bx-overlay-next, .bx-overlay-prev').toggle();
                    });
                } else {
                    removePagerFromCaption();
                    figures.find('.figure__caption').show();
                    $('.bx-overlay-next, .bx-overlay-prev').show();
                    figures.unbind();
                }
            });

            var figInMediaRes = function() {
                //for portrait mode images, set max height
                var figMedia = $('.inline-gallery .figure-full-width .figure__media');
                figMedia.each(function( index ) {
                    var imageWidth = $( this ).width();
                    var imageHeight = $( this ).height();
                    if(imageWidth <= imageHeight) {
                        $( this ).css('max-width', '100%');
                        $( this ).css('max-height', '620px');
                        $( this ).css('width', 'auto');
                        $( this ).css('height', 'auto');
                        $( this ).css("margin", '0 auto');
                    }
                });
            };

            figInMediaRes();

            var figCaptionSizing = function( image ) {
                var figCaptions = $('.inline-gallery .figure-full-width .figure__caption');
                figCaptions.each(function( index ) {
                    var previous = $( this ).prev().find('.figure__media'),
                    media = image || previous,
                    imageWidth = media.width(),
                    imageHeight = media.height();
                    if( $(this).parents('.gallery').size() > 0) {
                        $( this ).width(imageWidth);
                        $( this ).css("max-width", imageWidth);
                        if(imageWidth > 520) {
                            $( this ).css('padding-right', '30%');
                        }
                    } else {
                        if( previous.attr('src') === media.attr('src') ) {
                            if(imageWidth <= imageHeight) {
                                $( this ).css("max-width", imageWidth);
                            }
                        }
                    }
                });
            };

            //integrate tracking
            $( '.bx-wrapper' ).find( 'a' ).on( 'click', function(){
                var class_name = $( this ).attr( 'class' );
                var next = /^bx.+next/;
                var prev = /^bx.+prev/;
                if( next.exec(class_name) || prev.exec(class_name) ){
                    window.clickCount.webtrekk('hp.zm.slidegallery.showslide.');
                    window.clickCount.ga('hp.zm.slidegallery.showslide.');
                }
            });

            figCaptionSizing();
            slider.redrawSlider();
        });
    };
})(jQuery);
