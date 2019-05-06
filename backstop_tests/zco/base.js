let scenarios = [];
const urls = [
  'http://localhost:9090/campus/index',
  'http://localhost:9090/campus/article/01-countdown-studium',
  'http://localhost:9090/campus/article/02-beziehung-schluss-machen',
  'http://localhost:9090/campus/article/03-spartipps',
  'http://localhost:9090/campus/article/advertorial-onepage',
  'http://localhost:9090/campus/article/all-blocks',
  'http://localhost:9090/campus/article/authorbox',
  'http://localhost:9090/campus/article/column',
  'http://localhost:9090/campus/article/debate',
  'http://localhost:9090/campus/article/flexible-toc',
  'http://localhost:9090/campus/article/infografix',
  'http://localhost:9090/campus/article/infographic',
  'http://localhost:9090/campus/article/inline-gallery',
  'http://localhost:9090/campus/article/leserartikel',
  'http://localhost:9090/campus/article/paginated',
  'http://localhost:9090/campus/article/simple',
  'http://localhost:9090/campus/article/simple-with-nextread-leserartikel',
  'http://localhost:9090/campus/article/stoa',
  'http://localhost:9090/campus/article/video',
  'http://localhost:9090/campus/centerpage/advertorial',
  'http://localhost:9090/campus/centerpage/cardstack',
  'http://localhost:9090/campus/centerpage/cp-extra-tool-box',
  'http://localhost:9090/campus/centerpage/cp-of-cps',
  'http://localhost:9090/campus/centerpage/index',
  'http://localhost:9090/campus/centerpage/index-noimage',
  'http://localhost:9090/campus/centerpage/paginierung',
  'http://localhost:9090/campus/centerpage/servicelinks',
  'http://localhost:9090/campus/centerpage/teaser-advertorial',
  'http://localhost:9090/campus/centerpage/teaser-debate',
  'http://localhost:9090/campus/centerpage/teaser-follow-us',
  'http://localhost:9090/campus/centerpage/teaser-graphical',
  'http://localhost:9090/campus/centerpage/teaser-lead-cinema',
  'http://localhost:9090/campus/centerpage/teaser-lead-portrait',
  'http://localhost:9090/campus/centerpage/teaser-square',
  'http://localhost:9090/campus/centerpage/teaser-topic',
  'http://localhost:9090/campus/centerpage/teaser-topic-graphical',
  'http://localhost:9090/campus/centerpage/teaser-topic-variant',
  'http://localhost:9090/campus/centerpage/teaser-wide-large',
  'http://localhost:9090/campus/centerpage/teaser-wide-small',
  'http://localhost:9090/campus/centerpage/teasers',
  'http://localhost:9090/campus/centerpage/teasers-to-leserartikel',
  'http://localhost:9090/campus/centerpage/thema',
  'http://localhost:9090/campus/centerpage/tube'
];

urls.forEach(url => {
  scenarios.push({
    'label': url.replace('http://localhost:9090/', '').replace(/\//g, '_'),
    'cookiePath': '',
    'url': url,
    'referenceUrl': '',
    'readyEvent': '',
    'readySelector': '',
    'delay': 100,
    'hideSelectors': [],
    'removeSelectors': [
      '#pDebug'
    ],
    'hoverSelector': '',
    'clickSelector': '',
    'postInteractionWait': '',
    'selectors': [],
    'selectorExpansion': true,
    'misMatchThreshold': 0.1,
    'requireSameDimensions': true
  });
});

module.exports = scenarios;
