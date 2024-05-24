const scenarios = [
  {
    url: '/zeit-online/centerpage/index',
    selectors: ['header.header'],
  },
  {
    label: 'darkmode',
    url: '/zeit-online/centerpage/index',
    selectors: ['header.header'],
    onBeforeScript: 'prefers-color-scheme-dark.js',
  },
  {
    label: 'navigation-panorama',
    url: '/zeit-online/centerpage/zon-teaser-wide-panorama',
    selectors: ['header.header'],
  },
  {
    label: 'darkmode',
    url: '/zeit-online/centerpage/zon-teaser-wide-panorama',
    selectors: ['header.header'],
    onBeforeScript: 'prefers-color-scheme-dark.js',
  },
];

module.exports = scenarios;
