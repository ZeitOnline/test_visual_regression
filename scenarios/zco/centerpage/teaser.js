const scenarios = [
	{
		url: '/campus/centerpage/teaser-wide-small',
		selectors: ['.teaser-wide-small '],
	},
	{
		url: '/campus/centerpage/teaser-wide-large',
		selectors: ['.teaser-wide-large'],
	},
	{
		url: '/campus/centerpage/teaser-square',
		selectors: ['.teaser-square'],
	},
	{
		url: '/campus/centerpage/teaser-lead-portrait',
		selectors: ['.teaser-lead-portrait'],
	},
	{
		url: '/campus/centerpage/teaser-lead-cinema',
		selectors: ['.teaser-lead-cinema'],
	},
	{
		url: '/campus/centerpage/teaser-debate',
		selectors: ['.teaser-debate'],
	},
	{
		url: '/campus/centerpage/teaser-follow-us',
		selectors: ['.teaser-follow-us'],
		onBeforeScript: 'intercept-image.js',
		interceptImagePath: 'images/zco_cover.webp',
	},
];

module.exports = scenarios;
