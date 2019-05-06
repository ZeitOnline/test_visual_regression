let scenarios = [];
const urls = [
  'http://localhost:9090/campus/article/embed-header-cardstack',
  'http://localhost:9090/campus/article/embed-header-empty',
  'http://localhost:9090/campus/article/embed-header-image',
  'http://localhost:9090/campus/article/embed-header-quiz',
  'http://localhost:9090/campus/article/embed-header-raw',
  'http://localhost:9090/campus/article/embed-header-video'
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
