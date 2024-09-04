const scenarios = [];
const urls = [
	'http://localhost:9090/zeit-online/gallery/biga_1',
	'http://localhost:9090/zeit-online/gallery/england-meer-strand-menschen-fs',
	'http://localhost:9090/zeit-online/gallery/google-neuronale-netzwerke-fs',
	'http://localhost:9090/zeit-online/gallery/hitze-sommer-temperaturen-deutschland-fs',
	'http://localhost:9090/zeit-online/gallery/schrebergarten-gemeinschaft-glueck-fs',
	'http://localhost:9090/zeit-online/gallery/weltall',
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
