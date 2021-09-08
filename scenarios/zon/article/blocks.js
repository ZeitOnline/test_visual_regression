const waitTime = 6500;
const scenarios = [
  {
    url: '/zeit-online/article/inline-gallery',
    selectors: ['.gallery'],
    scrollToSelector: '.gallery',
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'gallery-image.jpg',
    postInteractionWait: 0,
  },
  {
    url: '/zeit-online/article/volumeteaser',
    selectors: ['.volume-teaser'],
    scrollToSelector: '.volume-teaser',
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'printcover.webp',
    postInteractionWait: waitTime,
  },
];

module.exports = scenarios;
