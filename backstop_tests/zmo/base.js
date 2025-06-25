const scenarios = [];
const host = 'http://localhost:9090';

const urls = [
	'/zeit-magazin/kpi',
	'/zeit-magazin/index',
	'/zeit-magazin/misc',
	'/zeit-magazin/teaser-card',
	'/zeit-magazin/teaser-fullwidth',
	'/zeit-magazin/teaser-landscape-large',
	'/zeit-magazin/teaser-landscape-small',
	'/zeit-magazin/teaser-mtb-square',
	'/zeit-magazin/teaser-print-cover',
	'/zeit-magazin/teaser-square-large',
	'/zeit-magazin/teaser-upright',
	'/zeit-magazin/teaser-upright-large',
];

urls.forEach(url => {
	scenarios.push({
		label: url,
		cookiePath: '',
		url: `${host}${url}`,
		referenceUrl: '',
		readyEvent: '',
		readySelector: '',
		delay: 100,
		hideSelectors: [],
		removeSelectors: [
			'#pDebug',
			'.comment-section',
			'.photocluster',
			'video',
			'.js-videoplayer',
			'.js-liveblog',
			'.image--processing',
		],
		hoverSelector: '',
		clickSelector: '',
		postInteractionWait: '',
		selectors: ['main'],
		selectorExpansion: true,
		misMatchThreshold: 0.1,
		requireSameDimensions: true,
	});
});

module.exports = scenarios;
