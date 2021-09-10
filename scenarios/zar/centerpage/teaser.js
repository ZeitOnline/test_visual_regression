const scenarios = [
  {
    url: '/arbeit/centerpage/teaser-small',
    selectors: ['.teaser-small'],
    selectorExpansion: true,
    expect: 6,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teaser-duo',
    selectors: ['.teaser-duo'],
    selectorExpansion: true,
    expect: 4,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teaser-quote',
    selectors: ['.teaser-quote'],
    selectorExpansion: true,
    expect: 4,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/julia-zange.webp',
  },
  {
    url: '/arbeit/centerpage/teasers',
    selectors: ['.teaser-lead'],
  },
  {
    url: '/arbeit/centerpage/teaser-debate',
    selectors: ['.debatebox-on-cp'],
  },
  {
    url: '/arbeit/centerpage/joblisting',
    selectors: ['.joblisting'],
    readySelector: '.joblisting__list[data-go="out"]',
  },
];

module.exports = scenarios;
