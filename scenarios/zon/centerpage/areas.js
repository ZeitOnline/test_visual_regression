const scenarios = [
  {
    label: 'buzzbox',
    url: '/zeit-online/centerpage/kpi',
    readySelector: '.kpi-accordion__button[aria-expanded]',
    delay: 200,
    selectors: ['main'],
    viewports: ['mobile'],
  },
  {
    label: 'buzzboard',
    url: '/zeit-online/centerpage/kpi',
    selectors: ['main'],
    viewports: ['tablet', 'desktop'],
  },
  {
    url: '/zeit-online/centerpage/zon-teaser-lead',
    selectors: ['.cp-area--lead'],
  },
];

module.exports = scenarios;
