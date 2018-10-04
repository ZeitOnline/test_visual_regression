let scenarios = [];
const host = 'http://localhost:9090';
const urls = [
  '/zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview',
];

urls.forEach(url => {
  scenarios.push({
    'label': url,
    'cookiePath': '',
    'url': `${host}${url}`,
    'referenceUrl': '',
    'readyEvent': '',
    'readySelector': '',
    'delay': 100,
    'hideSelectors': [],
    'removeSelectors': [
      '#pDebug',
      '.article__main-video--longform'
    ],
    'hoverSelector': '',
    'clickSelector': '',
    'postInteractionWait': '',
    'selectors': ['document'],
    'selectorExpansion': true,
    'misMatchThreshold': 0.1,
    'requireSameDimensions': true
  })
})

module.exports = scenarios;