const scenarios = [
  {
    url: '/zeit-online/article/simple',
    selectors: ['header.header'],
    viewports: ['mobile'],
  },
  {
    url: '/zeit-online/article/simple',
    readySelector: '.nav__ressorts--fitted',
    selectors: ['header.header'],
    viewports: ['tablet', 'desktop'],
  },
];

module.exports = scenarios;
