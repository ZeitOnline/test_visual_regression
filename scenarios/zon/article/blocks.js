const scenarios = [
	{
		url: '/zeit-online/article/inline-gallery',
		selectors: ['.gallery'],
		scrollToSelector: '.gallery',
		onBeforeScript: 'intercept-image.js',
		interceptImagePath: 'gallery-image.jpg',
	},
	{
		url: '/zeit-online/article/volumeteaser',
		selectors: ['.volume-teaser'],
		scrollToSelector: '.volume-teaser',
		onBeforeScript: 'intercept-image.js',
		interceptImagePath: 'printcover.webp',
	},
	{
		url: '/zeit-online/article/newslettersignup',
		selectors: ['.newsletter-signup'],
		selectorExpansion: true,
		expect: 3,
	},
];

module.exports = scenarios;
