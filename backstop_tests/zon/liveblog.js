const scenarios = [];
const urls = [
	'http://localhost:9090/zeit-online/liveblog/champions-league',
	'http://localhost:9090/zeit-online/liveblog/sonnenfinsternis',
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
