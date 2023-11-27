const scenarios = [
  {
    url: '/zeit-online/centerpage/index',
    selectors: ['footer.footer'],
  },
  {
    label: 'darkmode',
    url: '/zeit-online/centerpage/index',
    selectors: ['footer.footer'],
    onBeforeScript: 'prefers-color-scheme-dark.js',
  },
];

module.exports = scenarios;
