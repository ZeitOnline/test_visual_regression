const scenarios = [];
const urls = [
	'http://localhost:9090/zeit-online/centerpage/cardstack',
	'http://localhost:9090/zeit-online/centerpage/centerpage',
	'http://localhost:9090/zeit-online/centerpage/exclusive',
	'http://localhost:9090/zeit-online/centerpage/follow-us',
	'http://localhost:9090/zeit-online/centerpage/force-mobile-image',
	'http://localhost:9090/zeit-online/centerpage/liveblog',
	'http://localhost:9090/zeit-online/centerpage/podcast',
	'http://localhost:9090/zeit-online/centerpage/podcast-teaser',
	'http://localhost:9090/zeit-online/centerpage/podcast-teaser-fallback',
	'http://localhost:9090/zeit-online/centerpage/print-ressort',
	'http://localhost:9090/zeit-online/centerpage/print-ressort-with-campus',
	'http://localhost:9090/zeit-online/centerpage/register',
	'http://localhost:9090/zeit-online/centerpage/taglogo',
	'http://localhost:9090/zeit-online/centerpage/taglogo-d18',
	'http://localhost:9090/zeit-online/centerpage/teasers-to-arbeit',
	'http://localhost:9090/zeit-online/centerpage/teasers-to-brandeins',
	'http://localhost:9090/zeit-online/centerpage/teasers-to-campus',
	'http://localhost:9090/zeit-online/centerpage/tube',
	'http://localhost:9090/zeit-online/centerpage/volumeteaser',
	'http://localhost:9090/zeit-online/centerpage/zplus',
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
		selectors: ['html'],
		selectorExpansion: true,
		misMatchThreshold: 0.1,
		requireSameDimensions: true,
	});
});

module.exports = scenarios;
