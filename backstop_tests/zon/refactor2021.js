const scenarios = [];
const urls = [
	'http://localhost:9090/zeit-online/centerpage/kpi',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-gallery',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-gallery-variants',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-lead',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-panorama',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-podcast',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-podcast-lead',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-podcast-variants',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-poster',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-poster-video',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-square-author',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-standard',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-upright',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-video',
	'http://localhost:9090/zeit-online/centerpage/zon-teaser-wide',
	'http://localhost:9090/zeit-online/centerpage/teaser-to-wochenmarkt',
];

urls.forEach(url => {
	scenarios.push({
		label: url.replace('http://localhost:9090/', '').replace(/\//g, '_'),
		cookiePath: '',
		url: url,
		referenceUrl: '',
		readyEvent: '',
		readySelector: '',
		delay: 100,
		hideSelectors: [],
		removeSelectors: ['#pDebug'],
		hoverSelector: '',
		clickSelector: '',
		postInteractionWait: '',
		selectors: [],
		selectorExpansion: true,
		misMatchThreshold: 0.1,
		requireSameDimensions: true,
	});
});

module.exports = scenarios;
