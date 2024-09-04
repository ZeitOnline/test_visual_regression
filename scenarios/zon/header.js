const scenarios = [
	{
		url: '/zeit-online/article/simple',
		selectors: ['header.header'],
		viewports: ['mobile', 'tablet', 'desktop'],
	},
	{
		label: 'darkmode',
		url: '/zeit-online/article/simple',
		selectors: ['header.header'],
		viewports: ['mobile', 'tablet', 'desktop'],
		onBeforeScript: 'prefers-color-scheme-dark.js',
	},
];

module.exports = scenarios;
