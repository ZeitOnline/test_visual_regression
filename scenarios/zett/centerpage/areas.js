const scenarios = [
  {
    url: '/zett/centerpage/index',
    selectors: ['viewport'],
    viewports: [  'desktop'],
  },
  {
    url: '/zett/centerpage/index',
    selectors: ['.cp-region--standard'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    url: '/zett/centerpage/index',
    selectors: ['.cp-region--duo'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    url: '/zett/centerpage/index',
    selectors: ['.cp-region--trio'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    url: '/zett/centerpage/index',
    selectors: ['.cp-region--trio ~ .cp-region--trio'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
  {
    url: '/zett/centerpage/index',
    selectors: ['.cp-region--trio ~ .cp-region--trio ~ .cp-region--standard'],
    onBeforeScript: 'intercept-image.js',
    interceptImagePath: 'imageStub.jpg',
  },
];

module.exports = scenarios;
