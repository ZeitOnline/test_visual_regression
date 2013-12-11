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

	// list of possible ads
	// guess we need this configuration somewhere global accessible
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
		// top banner supplies: leaderboard
		topbanner_no_fp_no_wp: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			dcopt: 'ist',
			tile: 1,
			size: '728x90',
			keywords: ['iqadtile1', 'zeitonline', 'zeitmz', 'noiqdfireplace', 'noiqdwallpaper']
		},
		// scyscraper ad (hidden if wallpaper or fireplace is given)
		skyscraper: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			tile: 2,
			size: '120x600',
			keywords: ['iqadtile2', 'zeitonline', 'zeitmz']
		},
		mobile: function() {
			var sas_pageid = '54114/391248',
				sas_formatid = 13500,
				sas_target = '';
			if( typeof window.sasmobile === 'function') {
				window.sasmobile(sas_pageid,sas_formatid,sas_target);
			}
		},
		medrec_8: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			tile: 8,
			size: '300x250,300x600,300x100',
			keywords: ['iqadtile8', 'zeitmz', 'noiqdband']
		},
		medrec_10: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			tile: 10,
			size: '300x250,300x100',
			keywords: ['iqadtile10', 'zeitmz', 'noiqdband']
		}
	},
	// configuration of ad places aka. slots
	// one place can own n ads, differing by screen estate size
	places = {
		topbanner: {
			active_class: null,
			active_id: null,
			ads: [
				// desktop: full width
				{
					div_id: 'iqadtile1',
					min_width: 981,
					min_height: 0,
					ad: ads.topbanner
				},
				// desktop: not enough space for fireplace and wallpaper
				{
					div_id: 'iqadtile1',
					min_width: 728,
					max_width: 980,
					min_height: 0,
					ad: ads.topbanner_no_fp_no_wp
				}
			]
		},
		mobile_topbanner: {
			active_class: null,
			active_id: null,
			ads: [
				// mobile
				{
					div_id: 'sas_13500',
					div_class: 'ad__leaderboard--mobile',
					max_width: 727,
					min_width: 320,
					min_height: 0,
					callback: ads.mobile
				}
			]
		},
		skyscraper: {
			active_class: null,
			active_id: null,
			ads: [
				{
					div_id: 'iqadtile2',
					min_width: 728,
					min_height: 0,
					ad: ads.skyscraper
				}
			]
		},
		medrec_8: {
			active_class: null,
			active_id: null,
			ads: [{
				div_id: 'iqadtile8',
				min_width: 480,
				min_height: 0,
				ad: ads.medrec_8
			}]
		},
		medrec_10: {
			active_class: null,
			active_id: null,
			ads: [{
				div_id: 'iqadtile10',
				min_width: 480,
				min_height: 0,
				ad: ads.medrec_10
			}]
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
					slot.active_class = typeof(ad.div_class) !== "undefined" ? ad.div_class : "";
					slot.active_id = typeof(ad.div_id) !== "undefined"? ad.div_id : "";
					if( typeof(ad.ad) !== "undefined" ) {
						slot.active_ad = ad.ad;
					}
					if( typeof(ad.callback) === "function" ) {
						// add callback to the onload event
						window[ addEventListener ? 'addEventListener' : 'attachEvent' ]( addEventListener ? 'load' : 'onload', ad.callback );
					}
					return slot;
			} else {
				_results.push(void 0);
			}
		}
		return _results;
	};

	return {
		printable_ad_place: function( place ) {
			var slot = prepare_slot( places[place] ),
				ad = '';
			if( typeof slot.active_id !== "undefined" ) {
				if( typeof(slot.active_ad) !== 'undefined' ) {
					ad = '<script src="';
					ad += slot.active_ad.url;
					ad += slot.active_ad.fragment;
					if( typeof slot.active_ad.dcopt !== 'undefined' ) {
						ad+= ';dcopt=' + slot.active_ad.dcopt;
					}
					ad += ';tile=' + slot.active_ad.tile;
					ad += ';' + win.n_pbt;
					ad += 'sz=' + slot.active_ad.size;
					ad += ';kw=' + slot.active_ad.keywords.join(",");
					ad += ',' + win.iqd_TestKW;
					ad += ';ord=' + win.IQD_varPack.ord;
					ad += '?" type="text/javascript"><\/script>';
				}
				var div = '<div class="' + slot.active_class + '" id="' + slot.active_id + '">%1</div>';
				div = div.replace("%1", ad);
				return div;
			} else {
				// empty string returned to deactivate document.write()
				return "";
			}
		}
	};

}( window );