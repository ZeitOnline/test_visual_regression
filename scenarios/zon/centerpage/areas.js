const scenarios = [
  {
    label: 'buzzbox',
    url: '/zeit-online/centerpage/kpi',
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
];

module.exports = scenarios;
