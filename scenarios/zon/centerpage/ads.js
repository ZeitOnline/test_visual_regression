const scenarios = [
  {
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['.ad-container[data-type="desktop"]'],
    selectorExpansion: true,
    expect: 13,
    viewports: ['desktop', 'tablet']
  },
  {
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['.ad-container[data-type="mobile"]'],
    selectorExpansion: true,
    expect: 10,
    viewports: ['mobile']
  },
  {
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['.ad-container--in-app[data-type="mobile"]'],
    selectorExpansion: true,
    expect: 10,
    onBeforeScript: 'appUserAgent.js',
    viewports: ['mobile', 'tablet']
  },
];

module.exports = scenarios;
