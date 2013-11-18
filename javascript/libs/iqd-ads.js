/**
*
* Konfigurationsvariablen der IQD
*
**/
var iqd_Loc = (top==self) ? window.location : parent.location;
var iqd_Domain = iqd_Loc.href.toLowerCase();
// var iqd_TestKW = (iqd_Domain.indexOf('iqtest=true')> -1) ? 'iqtest' : 'iqlive';   
var iqd_TestKW = 'iqtest';
var IQD_varPack = {
    iqdSite: 'zeitmz',
    iqdRessort: '',
    ord: Math.random()*10000000000000000,
    iqdSiteInfo: [[980, 0, -20], [0, 0, 960], [0, 0, 960], ['center', 'fullBodyBg'], ['y', 'y', 'y']],
    iqdCountSkyReq: parseInt(0, 10),
    iqdEnableSky: 'neutral'
};
var ord = (Math.random()*100000);
var n_pbt = "";