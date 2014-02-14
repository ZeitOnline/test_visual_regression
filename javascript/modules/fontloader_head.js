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
			path: '/css/standalone-fonts/base.css',
			version: "1.0"
		},
		{
			identifier: 'quotes',
			selector: '.quote, .quote--loud',
			path: '/css/standalone-fonts/quotes.css',
			version: "1.0"
		}
	];

	this.storage_base_string = 'de.zeit.zmo__webfonts--';
	this.storage_version_suffix = '--version';
	this.scheduled_fonts = [];

	// detect modern browsers that support woff
	this.modern_browser = ('querySelector' in document) && ('localStorage' in window) && ('addEventListener' in window) && (window.document.documentElement.className.indexOf( "lt-ie9" ) === -1);
	this.inject_ref = window.document.getElementsByTagName("link")[0];

	// queue font pack download for later
	this.lazy_load_fonts = function(pack) {
		this.scheduled_fonts.push(pack);
	};

	// create a style tag in the <head> filled with raw font-face declarations
	this.append_css = function(style) {
		var style_tag = window.document.createElement("style");
		style_tag.innerHTML = style;
		if(this.inject_ref && this.inject_ref.parentNode) {
			this.inject_ref.parentNode.insertBefore(style_tag, this.inject_ref);
		}
	};

	// load fonts from localstorage or queue up for lazy loading
	this.init_fonts = function() {
		// run through all font packs in the dictionary
		for (var i in this.font_dictionary) {
			if (i) {
				var pack = this.font_dictionary[i];
				var stored_version = localStorage.getItem(this.storage_base_string + pack.identifier + this.storage_version_suffix);
				pack.data = localStorage.getItem(this.storage_base_string + pack.identifier);
				if (pack.data) {
					if (pack.version === stored_version) {
						// font is in localstorage, drop data in style tag immediately
						this.append_css(pack.data);
					} else {
						// font is in local storage, but outdated, queue font download for later
						this.lazy_load_fonts(this.font_dictionary[i]);
					}
				} else {
					// not in localstorage, queue font download for later
					this.lazy_load_fonts(this.font_dictionary[i]);
				}
			}
		}
	};

	// only load fonts if modern browser
	if (this.modern_browser) {
		this.init_fonts();
	}

	return this;
})();