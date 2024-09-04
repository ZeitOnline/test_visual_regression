const scenarios = [];
const urls = [
	{
		url: 'http://localhost:9090/zeit-online/article/authorbox',
		selectors: ['.portraitbox', '.authorbox'],
	},
	{
		url: 'http://localhost:9090/zeit-online/article/portraitbox',
		selectors: ['.portraitbox', '.authorbox'],
	},
	{
		url: 'http://localhost:9090/zeit-online/printbox',
		selectors: ['.print-box', '.authorbox'],
	},
];

urls.forEach(url => {
	scenarios.push({
		label: url.url.replace('http://localhost:9090/', '').replace(/\//g, '_'),
		cookiePath: '',
		url: url.url,
		referenceUrl: '',
		readyEvent: '',
		readySelector: '',
		delay: 100,
		hideSelectors: [],
		removeSelectors: ['#pDebug'],
		hoverSelector: '',
		clickSelector: '',
		postInteractionWait: '',
		selectors: url.selectors,
		selectorExpansion: true,
		misMatchThreshold: 0.1,
		requireSameDimensions: true,
	});
});

module.exports = scenarios;
