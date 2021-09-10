const scenarios = [
  {
    label: 'click-bookmark',
    url: '/zeit-online/centerpage/zon-teaser-standard',
    clickSelectors: ['.bookmark-icon'],
    selectors: ['viewport'],
  },
  {
    label: 'click-bildrechte',
    url: '/zeit-online/centerpage/zon-teaser-snapshot',
    scrollToSelector: '.footer',
    readySelector: '.js-image-copyright-footer',
    clickSelectors: ['.js-image-copyright-footer'],
    postInteractionWait: 1000,
    selectors: ['viewport'],
    viewports: ['tablet', 'desktop'],
  },
];

module.exports = scenarios;
