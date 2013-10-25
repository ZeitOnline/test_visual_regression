// IQD_AdProbeTag
var wlCus = "13004,13002,13033,13003,13005,12998";
var wlOrd = new Date().getTime();

try{
	document.write( '<scr' + 'ipt type="text/javascript" language="JavaScript" src="//req.connect.wunderloop.net/AP/1624/6625/12996/js?cus=' + wlCus + '&ord=' + wlOrd + '"><\/scr'+'ipt>' );
}catch( err ) { }
					

// IQD Audiencescience
var rsi_segs = [];
var segs_beg = document.cookie.indexOf( 'rsi_segs=' );

if( segs_beg >= 0 ){
	segs_beg = document.cookie.indexOf( '=', segs_beg ) + 1;

	if( segs_beg > 0 ){
		var segs_end = document.cookie.indexOf( ';', segs_beg );
		if( segs_end === -1 ){ segs_end = document.cookie.length };
		rsi_segs = document.cookie.substring( segs_beg,segs_end ).split( '|' );
	}
}

var segLen = 20;
var segQS = "";

if( rsi_segs.length < segLen ){ segLen = rsi_segs.length; }

for( var i=0; i<segLen; i++ ){
	segQS += ( "rsi" + "=" + rsi_segs[i] + ";" );
}

// IQD varPack
var IQD_varPack = {
	iqdSite: 'zol',
	iqdRessort: '',
	ord: Math.random()*10000000000000000,
	iqdSiteInfo: [[980, 0, 0], [0, 0, 980], [0, 0, 980], ['center', 'fullBodyBg'], ['y', 'y', 'y']],
	iqdCountSkyReq: parseInt(0),
	iqdEnableSky: 'neutral'
};

// IQD variable test
var iqd_Loc = (top === self) ? window.location : parent.location;
var iqd_Domain = iqd_Loc.href.toLowerCase();
var iqd_TestKW = ( iqd_Domain.indexOf( 'iqadtest=true' ) > -1 ) ? 'iqadtest' : 'iqlive';
	
var n_pbt = "";
      
