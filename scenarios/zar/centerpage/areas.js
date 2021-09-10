const scenarios = [
  {
    url: '/arbeit/centerpage/teaser-topic',
    selectors: ['.cp-region--topic'],
  },
  {
    url: '/arbeit/centerpage/teaser-topiccluster',
    selectors: ['main'],
    hoverSelectors: ['.teaser-topiccluster__heading-link'],
  },
  {
    url: '/arbeit/centerpage/thema-minimal',
    selectors: ['.cp-region--has-headerimage'],
  },
];

module.exports = scenarios;
