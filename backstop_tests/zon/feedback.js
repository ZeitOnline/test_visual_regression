const scenarios = [];
const urls = [
	'http://localhost:9090/autoren/S/Thomas_Strothjohann/index/feedback',
	'http://localhost:9090/zeit-online/article/feedback',
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
		selectors: ['document'],
		selectorExpansion: true,
		misMatchThreshold: 0.1,
		requireSameDimensions: true,
	});
});

module.exports = scenarios;
