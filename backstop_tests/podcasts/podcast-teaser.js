let scenarios = []
const urls = [
  'http://localhost:9090/zeit-online/centerpage/podcast-teaser',
  'http://localhost:9090/arbeit/centerpage/teaser-podcast'
]

urls.forEach( url => {
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
    'selectors': ['.teaser-podcast'],
    'selectorExpansion': true,
    'misMatchThreshold': 0.1,
    'requireSameDimensions': true
  });
});

module.exports = scenarios;