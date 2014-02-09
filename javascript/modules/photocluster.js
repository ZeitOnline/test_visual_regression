/* global console, define */

define(['packery', 'jquery'], function() {

  var init = function() {
    var $cluster = $('.photocluster');
    if ($cluster) {
      var $photos = $cluster.children();
      var classes = ['size-s', 'size-m', 'size-l'];

      // run through all photo boxes
      $photos.each(function(idx, photo){
        var $photo = $(photo);
        // add random sizing class
        $photo.addClass(classes[Math.floor(Math.random()*classes.length)]);
        // find responsive image container within packery block
        var $rimg = $photo.find('img, noscript').eq(0);
        if ($rimg.length === 1) {
          // adjust height of packery block to ratio of image
          // TODO: debounced recalculation on resize (see images.js for example)
          $photo.css('height', $photo.width()/$rimg.data('ratio') + 10);
        }
      });

      // initialize packery
      $cluster.packery({
        itemSelector: '.photocluster__item',
        gutter: 0
      });
    }
  };

  return {
    init: init
  };

});