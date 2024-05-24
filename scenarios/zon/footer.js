const scenarios = [
  {
    url: '/zeit-online/article/simple',
    selectors: ['footer.footer'],
  },
  {
    url: '/zeit-online/centerpage/index',
    selectors: ['footer.footer'],
  },
  {
    label: 'darkmode',
    url: '/zeit-online/article/simple',
    selectors: ['footer.footer'],
    onBeforeScript: 'prefers-color-scheme-dark.js',
  },
];

module.exports = scenarios;
