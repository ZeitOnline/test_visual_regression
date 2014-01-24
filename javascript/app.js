/* globals require */

require.config({
	paths: {
    "jquery": "libs/jquery-1.10.2.min",
		"underscore": "libs/underscore-min",
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
	},{
		'modules/plugins/jquery.enablepopups': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.enablePopups'
		}
	},{
		'modules/plugins/jquery.backgroundvideo': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.backgroundVideo'
		}
    },{
		'modules/plugins/jquery.enablepopups': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.enablePopups'
		}
    },{
        'modules/plugins/jquery.animatescroll': {
            deps: [ 'jquery' ],
            exports: 'jQuery.fn.animateScroll'
        }
	}]
});

require(['modules/fontloader', 'modules/breadcrumbs', 'modules/tabs', 'modules/comments', 'modules/main-nav', 'modules/adloader', 'modules/images', 'sjcl', 'modules/plugins/jquery.switchvideo', 'modules/plugins/jquery.backgroundvideo', 'modules/plugins/jquery.enablepopups', 'modules/plugins/jquery.animatescroll', 'libs/jquery.bxslider'],
  function(fontloader, breadcrumbs, tabs, comments, main_nav, adloader, images) {
    fontloader.init();
    main_nav.init();
    breadcrumbs.init();
    tabs.init();
    comments.init();
    adloader.init();
    images.init();
    $( "figure[data-video]" ).switchVideo();
    $( "div[data-backgroundvideo]" ).backgroundVideo();
    $( "a.js-has-popup" ).enablePopups();
    $( "figure.gallery__inline").bxSlider();
    $( "a[href^='#']" ).animateScroll();
});
