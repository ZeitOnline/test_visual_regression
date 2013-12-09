/*
*
* resize-ads.js
* loads ads in the needed size depending on screen estate
*
*/
var resizeAds = function( win ) {

	// IQD varPack
	win.IQD_varPack = {
		iqdSite: 'zol',
		iqdRessort: '',
		ord: Math.random()*10000000000000000,
		iqdSiteInfo: [[980, 0, 0], [0, 0, 980], [0, 0, 980], ['center', 'fullBodyBg'], ['y', 'y', 'y']],
		iqdCountSkyReq: parseInt(0,10),
		iqdEnableSky: 'neutral'
	};
	// IQD variable test
	win.iqd_Loc = (win.top===win.self) ? window.location : parent.location;
	win.iqd_Domain = win.iqd_Loc.href.toLowerCase();
	win.iqd_TestKW = (win.iqd_Domain.indexOf('iqadtest=true')> -1) ? 'iqadtest' : 'iqlive';

	var console = window.console || {};

	// privates
	var ads = {
		// top banner supplies: leaderboard, wallpaper and fireplace
		topbanner: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			dcopt: 'ist',
			tile: 1,
			size: '728x90',
			keywords: ['iqadtile1', 'zeitonline', 'zeitmz']
		},
		// scyscraper ad (hidden if wallpaper or fireplace is given)
		skyscraper: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			tile: 2,
			size: '120x600',
			keywords: ['iqadtile2', 'zeitonline', 'zeitmz']
		}
	},
	places = {
		topbanner: {
			active_class: null,
			active_ad: null,
			ads: [
				{
					div_class: 'iqadtile1',
					min_width: 728,
					min_height: 0,
					ad: ads.topbanner
				}
			]
		},
		skyscraper: {
			active_class: null,
			active_ad: null,
			ads: [
				{
					div_class: 'iqadtile2',
					min_width: 728,
					min_height: 0,
					ad: ads.skyscraper
				}
			]
		}
	},
	prepare_slot = function( slot ) {
		var ad, _i, _len, _ref, _results;
		_ref = slot.ads.slice(0).reverse();
		_results = [];
				
		for(_i = 0, _len = _ref.length; _i < _len; _i++ ){
			ad = _ref[_i];
			if( !ad.max_width ){
				ad.max_width = 5000;
			}
			if (window.innerWidth >= ad.min_width &&
				window.innerHeight >= ad.min_height &&
				window.innerWidth <= ad.max_width) {
					slot.active_class = ad.div_class;
					slot.active_ad = ad.ad;
					return slot;
			} else {
				_results.push(void 0);
			}
		}
		return _results;
	};

	return {
		printable_ad_place: function( place ) {
			var slot = prepare_slot( places[place] );
			var ad = '<script src="';
			ad += slot.active_ad.url;
			ad += slot.active_ad.fragment;
			ad += ';tile=' + slot.active_ad.tile;
			ad += ';' + win.n_pbt;
			ad += ';sz=' + slot.active_ad.size;
			ad += ';kw=' + slot.active_ad.keywords.join(",");
			ad += ',' + win.iqd_TestKW;
			ad += ';ord=' + win.IQD_varPack.ord;
			ad += '?" type="text/javascript"><\/script>';
			var div = '<div class="' + slot.active_class + '">%1</div>';
			div = div.replace("%1", ad);
			return div;
		}
	};

}( window );