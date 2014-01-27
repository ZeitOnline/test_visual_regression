/* globals require */

require.config({
	paths: {
		"jquery": "libs/jquery-1.10.2.min",
		"sjcl": "libs/sjcl",
		"bxSlider": 'libs/jquery.bxslider',
		"underscore": "libs/underscore-min"
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
		'modules/plugins/jquery.inlinegallery': {
			deps: [ 'jquery', 'bxSlider' ],
			exports: 'jQuery.fn.inlinegallery'
		}
    },{
        'modules/plugins/jquery.animatescroll': {
            deps: [ 'jquery' ],
            exports: 'jQuery.fn.animateScroll'
        }
	}]
});

require([
	'jquery',
	'modules/fontloader',
	'modules/breadcrumbs',
	'modules/tabs',
	'modules/comments',
	'modules/main-nav',
	'modules/images',
	'modules/supplement',
	'sjcl',
	'modules/plugins/jquery.switchvideo',
	'modules/plugins/jquery.backgroundvideo',
	'modules/plugins/jquery.enablepopups',
	'bxSlider',
	'modules/plugins/jquery.inlinegallery',
    'modules/plugins/jquery.animatescroll'
	],
	function(jQuery, fontloader, breadcrumbs, tabs, comments, main_nav, images, supplement) {
		fontloader.init();
		main_nav.init();
		breadcrumbs.init();
		tabs.init();
		comments.init();
		images.init();
		supplement.init();
		$( "figure[data-video]" ).switchVideo();
		$( "div[data-backgroundvideo]" ).backgroundVideo();
		$( "a.js-has-popup" ).enablePopups();
		$( ".inline-gallery" ).inlinegallery();
        $( "a[href^='#']" ).animateScroll();
	}
);
