const scenarios = [
  {
    url: '/zeit-magazin/article/inline-gallery',
    selectors: ['.gallery'],
    scrollToSelector: '.gallery',
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'gallery-image.jpg',
  },
  {
    url: '/zeit-magazin/article/volumeteaser',
    selectors: ['.volume-teaser'],
    scrollToSelector: '.volume-teaser',
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'zeit-wissen-cover.webp',
  },
];

module.exports = scenarios;
