const scenarios = [
  {
    label: 'click-bookmark',
    url: '/zeit-online/centerpage/zon-teaser-standard',
    clickSelectors: ['.bookmark-icon'],
    selectors: ['viewport'],
  },
  {
    label: 'click-hamburger',
    url: '/zeit-online/centerpage/zon-teaser-snapshot',
    clickSelectors: ['.header__menu-link'],
    postInteractionWait: 2000,
    selectors: ['viewport'],
    viewports: ['mobile'],
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
