/* globals require */

require.config({
	paths: {
		"jquery": "libs/jquery-1.10.2.min",
		"sjcl": "libs/sjcl"
	},
	shim: [{
		'libs/jquery.switchvideo': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.switchVideo'
		}
	},{
		'libs/jquery.bxslider': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.bxSlider'
		}
	}]
});

require([
	'modules/fontloader',
	'modules/breadcrumbs',
	'modules/tabs',
	'modules/comments',
	'modules/main-nav',
	'modules/adloader',
	'modules/images',
	'sjcl',
	'modules/plugins/jquery.switchvideo',
	'libs/jquery.bxslider'
	],
  function(fontloader, breadcrumbs, tabs, comments, main_nav, adloader, images) {
    fontloader.init();
    main_nav.init();
    breadcrumbs.init();
    tabs.init();
    comments.init();
    adloader.init();
    images.init();
	$( "figure[data-video]" ).switchVideo();
	$( "figure.gallery__inline").bxSlider();
});