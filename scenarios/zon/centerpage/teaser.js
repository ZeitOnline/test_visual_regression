const scenarios = [
  {
    url: '/zeit-online/centerpage/zon-teaser-wide',
    selectors: ['.zon-teaser-wide'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-poster',
    selectors: ['.zon-teaser-poster'],
    selectorExpansion: true,
    expect: 4,
  },
  {
    label: 'podcast',
    url: '/zeit-online/centerpage/zon-teaser-podcast',
    selectors: ['.zon-teaser-standard--podcast'],
  },
  {
    label: 'podcast',
    url: '/zeit-online/centerpage/zon-teaser-podcast-lead',
    selectors: ['.teaser-podcast-lead'],
  },
  {
    label: 'podcast',
    url: '/zeit-online/centerpage/zon-teaser-podcast-variants',
    selectors: ['article[class*="podcast"]'],
    selectorExpansion: true,
    expect: 15
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
  {
    url: '/zeit-online/centerpage/zon-teaser-snapshot',
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-square',
    selectors: ['.zon-teaser-square'],
    selectorExpansion: true,
    expect: 18,
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-upright',
    selectors: ['.zon-teaser-upright'],
    readySelector: '.zon-teaser-upright img',
    selectorExpansion: true,
    expect: 8,
  },
  {
    url: '/zeit-online/centerpage/joblisting',
    selectors: ['.joblisting'],
  }
];

module.exports = scenarios;
