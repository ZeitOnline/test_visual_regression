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
  {
    url: '/arbeit/centerpage/newslettersignup',
    selectors: ['.newsletter-signup'],
    expect: 4,
    selectorExpansion: true,
  },
  {
    url: '/arbeit/centerpage/teaser-topic',
    selectors: ['.teaser-topic'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teasers',
    selectors: ['.jobbox-dropdown'],
  },
  {
    url: '/arbeit/centerpage/teasers',
    selectors: ['.teaser-topiccluster'],
  },
  {
    url: '/arbeit/centerpage/teasers-to-zplus-registration',
    selectors: ['[data-zplus="zplus-register"]'],
    selectorExpansion: true,
    expect: 9,
  },
  {
    url: '/arbeit/centerpage/teasers-to-zplus-abo',
    selectors: ['[data-zplus="zplus"]'],
    selectorExpansion: true,
    expect: 9,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teaser-advertorial',
    selectors: ['.teaser-duo--advertorial'],
    expect: 2,
    selectorExpansion: true,
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teasers-to-ads',
    selectors: ['.teaser-duo--verlagsangebot'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teasers-to-ads',
    selectors: ['.teaser-small--advertorial'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
  {
    url: '/arbeit/centerpage/teasers-to-ads',
    selectors: ['.teaser-topic'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'images/blue.png',
  },
];

module.exports = scenarios;
