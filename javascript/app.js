/* globals require */

require.config({
  paths: {
    "jquery": "libs/jquery-1.10.2.min"
  }
});

require(['modules/fontloader'], function(fontloader) {
  fontloader.init();
});