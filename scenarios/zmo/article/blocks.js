const scenarios = [
  {
    url: '/zeit-magazin/article/inline-gallery',
    selectors: ['.gallery'],
    scrollToSelector: '.gallery',
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'gallery-image.jpg',
    postInteractionWait: 0,
  },
  {
    url: '/zeit-magazin/article/volumeteaser',
    selectors: ['.article'],
    scrollToSelector: '.volume-teaser',
    postInteractionWait: 7000,
  },
];

module.exports = scenarios;
