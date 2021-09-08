const waitTime = 6500;
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
    selectors: ['.volume-teaser'],
    scrollToSelector: '.volume-teaser',
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'zeit-wissen-cover.webp',
    postInteractionWait: waitTime,
  },
];

module.exports = scenarios;
