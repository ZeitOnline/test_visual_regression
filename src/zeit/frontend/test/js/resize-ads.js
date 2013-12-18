// seems to be wrong, todo: implement karma into py.text
var assert = chai.assert;
describe('Ad Script', function() {
	describe('#prepare_slot', function(){
		it('should return -1 when the value is not present', function() {
			var script = '<div class="iqadtile1"><script src="http://ad.de.doubleclick.net/adj/zeitonline/zolmz;tile=1;;sz=728x90;kw=iqadtile1,zeitonline,zeitmz,iqlive;ord=6104680004063994?" type="text/javascript"></script></div>';
			assert.equal(script, resizeAds.printable_ad_place('topbanner'));
		});
	});
});