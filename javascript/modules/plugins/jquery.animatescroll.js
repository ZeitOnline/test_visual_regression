/* global console, alert */
(function($){

  $.fn.animateScroll = function() {

    //run through links that jump to anchors
    $(this).each(function(){
      $(this).click(function(e) {
        e.preventDefault();
        var anchor = $(this).attr('href').replace('#','');
        $('html, body').animate({
          scrollTop: $('a[name='+anchor+']').eq(0).offset().top
        }, 500);
      });
    });

  };
})(jQuery);
