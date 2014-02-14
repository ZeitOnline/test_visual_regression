/* global console, alert */

/**
 * font loader setup
 */
window.FontLoader = (function() {
	// set up all font packages we need
	this.font_dictionary = [
		{
			identifier: 'base',
			selector: null,
			has_priority: true,
			path: '/css/standalone-fonts/base.css'
		},
		{
			identifier: 'quotes',
			selector: '.quote, .quote--loud',
			has_priority: false,
			path: '/css/standalone-fonts/quotes.css'
		}
	];

	this.ua = window.navigator.userAgent;
	this.storage_base_string = 'de.zeit.zmo__webfonts--';

	// detect old browsers that won’t support woff anyways
	this.is_old_browser = 'querySelector' in document && 'localStorage' in window && 'addEventListener' in window && this.ua.indexOf( "Android" ) > -1 && this.ua.indexOf( "like Gecko" ) > -1 && this.ua.indexOf( "Chrome" ) === -1 || window.document.documentElement.className.indexOf( "lt-ie9" ) > -1;
	this.inject_ref = window.document.getElementsByTagName( "link" )[0];

	this.fonts_loaded = false;

	return this;
})();