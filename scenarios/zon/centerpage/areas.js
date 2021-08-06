const scenarios = [
  {
    label: 'buzzbox',
    url: '/zeit-online/hp-rebrush-2019/kpi',
    readySelector: '.kpi-accordion__button[aria-expanded]',
    delay: 200,
    selectors: ['main'],
    viewports: ['mobile'],
  },
  {
    label: 'buzzboard',
    url: '/zeit-online/hp-rebrush-2019/kpi',
    selectors: ['main'],
    viewports: ['tablet', 'desktop'],
  },
  {
    url: '/zeit-online/hp-rebrush-2019/zon-teaser-lead',
    selectors: ['.cp-area--lead'],
  },
];

module.exports = scenarios;
