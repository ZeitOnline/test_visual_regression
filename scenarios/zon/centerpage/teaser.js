const scenarios = [
  {
    url: '/zeit-online/centerpage/zon-teaser-wide',
    selectors: ['.zon-teaser-wide'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-poster',
    selectors: ['.zon-teaser-poster'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-podcast',
    selectors: ['.zon-teaser-standard--podcast'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-podcast-lead',
    selectors: ['.teaser-podcast-lead'],
  },
  {
    url: '/zeit-online/centerpage/index-with-classic',
    selectors: ['.zon-teaser-classic'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-classic',
    selectors: ['.zon-teaser-classic'],
    selectorExpansion: true,
    expect: 12
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-classic-video',
    selectors: ['.zon-teaser-classic'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-column',
    selectors: ['.zon-teaser-classic'],
    selectorExpansion: true,
    expect: 12
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-standard',
    selectors: ['.zon-teaser-standard'],
    selectorExpansion: true,
    expect: 26,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-flat',
    selectors: ['article[class^="zon-teaser-flat"]'],
    selectorExpansion: true,
    expect: 10,
    postInteractionWait: 1000,
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-gallery',
    selectors: ['article'],
    selectorExpansion: true,
    expect: 6,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    label: 'region-lead',
    url: '/zeit-online/centerpage/zon-teaser-lead',
    selectors: ['.cp-region--lead'],
    selectorExpansion: true,
    expect: 5,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-panorama',
    selectors: ['.zon-teaser-panorama'],
  },
];

module.exports = scenarios;
