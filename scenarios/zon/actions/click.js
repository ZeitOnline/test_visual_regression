const scenarios = [
  {
    label: 'click-bookmark',
    url: '/zeit-online/centerpage/zon-teaser-standard',
    clickSelectors: ['button.bookmark'],
    selectors: ['viewport'],
  },
  {
    label: 'click-hamburger',
    url: '/zeit-online/centerpage/zon-teaser-standard',
    clickSelectors: ['a.navigation__button--account'],
    postInteractionWait: 2000,
    selectors: ['viewport'],
    viewports: ['mobile'],
  },
  {
    label: 'click-bildrechte',
    url: '/zeit-online/centerpage/zon-teaser-standard',
    scrollToSelector: '.footer',
    readySelector: '.js-image-copyright-dialog',
    clickSelectors: ['.js-image-copyright-dialog'],
    postInteractionWait: 1000,
    selectors: ['viewport'],
    viewports: ['tablet', 'desktop'],
  },
  {
    label: 'click-topicheader',
    url: '/thema/manualtopic',
    postInteractionWait: 1000,
    scrollToSelector: '.wrappable__button--more',
    readySelector: '.wrappable__button--more',
    clickSelectors: ['.wrappable__button--more'],
    selectors: ['document'],
  }
];

module.exports = scenarios;
