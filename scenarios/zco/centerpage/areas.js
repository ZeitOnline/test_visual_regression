const scenarios = [
  {
    url: '/campus/centerpage/teaser-topic-variant',
    selectors: ['.cp-region--topic'],
  },
  {
    url: '/campus/centerpage/thema',
    selectors: ['.cp-region--has-headerimage'],
  },
  {
    url: '/campus/centerpage/teaser-topic-graphical',
    selectors: ['.cp-area--topic-graphical'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
];

module.exports = scenarios;
