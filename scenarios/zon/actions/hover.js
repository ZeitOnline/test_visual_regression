const scenarios = [
  {
    label: 'hover-nav-more',
    url: '/zeit-online/centerpage/zon-teaser-snapshot',
    hoverSelectors: ['.nav__ressorts-item--more', '#more-ressorts .nav__ressorts-item--zeitmagazin'],
    selectors: ['document'],
    viewports: ['tablet', 'desktop'],
  },
  {
    label: 'hover-classified-more',
    url: '/zeit-online/centerpage/zon-teaser-snapshot',
    hoverSelectors: ['.nav__classifieds-item--has-dropdown', '#mehr .nav__dropdown-item--urlaubsziele'],
    selectors: ['document'],
    viewports: ['tablet', 'desktop'],
  },
];

module.exports = scenarios;
