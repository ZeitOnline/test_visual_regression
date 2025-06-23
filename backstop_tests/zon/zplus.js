const scenarios = [];
const urls = [
	// form_paid
	'http://localhost:9090/zeit-online/article/01?C1-Meter-Status=always_paid',
	// form_register
	'http://localhost:9090/zeit-online/article/01?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
	// core:zplus-badge
	'http://localhost:9090/zeit-magazin/article/header-default',
	// teaser zplus-badge ( red and grey)
	'http://localhost:9090/zeit-online/teaser-square-setup',
	// default card
	'http://localhost:9090/zeit-magazin/teaser-card',
	// nav extra item
	'http://localhost:9090/zeit-online/article/01',
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
