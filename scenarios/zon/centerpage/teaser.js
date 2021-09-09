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
];

module.exports = scenarios;
