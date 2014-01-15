/* globals require */

require.config({
	paths: {
    "jquery": "libs/jquery-1.10.2.min"
	},
	shim: {
		'modules/plugins/jquery.switchvideo': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.switchVideo'
		},
    'modules/plugins/jquery.enablepopups': {
      deps: [ 'jquery' ],
      exports: 'jQuery.fn.enablePopups'
    }
	}
});

require(['modules/fontloader', 'modules/breadcrumbs', 'modules/tabs', 'modules/comments', 'modules/main-nav', 'modules/adloader', 'modules/plugins/jquery.switchvideo', 'modules/plugins/jquery.enablepopups'],
  function(fontloader, breadcrumbs, tabs, comments, main_nav, adloader) {
    fontloader.init();
    main_nav.init();
    breadcrumbs.init();
    tabs.init();
    comments.init();
    adloader.init();
    $( "figure[data-video]" ).switchVideo();
		$( "a.js-has-popup" ).enablePopups();
});