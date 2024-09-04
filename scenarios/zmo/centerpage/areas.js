const scenarios = [
	{
		url: '/zeit-magazin/wochenmarkt/area-discover',
		selectors: ['.cp-area--discover'],
		onBeforeScript: 'intercept-image.js',
		interceptImagePath: 'imageStub.jpg',
	},
	{
		url: '/zeit-magazin/teaser-mtb-square',
		selectors: ['main'],
		onBeforeScript: 'intercept-image.js',
		interceptImagePath: 'imageStub.jpg',
	},
	{
		label: 'buzzboard',
		url: '/zeit-magazin/kpi',
		selectors: ['main'],
		viewports: ['tablet', 'desktop'],
	},
];

module.exports = scenarios;
