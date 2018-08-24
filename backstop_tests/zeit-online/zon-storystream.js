let scenarios = [];
const urls = [
    'http://localhost:9090/zeit-online/storystream/articles/grexit-griechenland-euro-zone',
    'http://localhost:9090/zeit-online/storystream/articles/griechenland-referendum-oxi',
    'http://localhost:9090/zeit-online/storystream/articles/syriza-tsipras-parlamentswahl',
    'http://localhost:9090/zeit-online/storystream/dummy',
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
    'selectors': ['html'],
    'selectorExpansion': true,
    'misMatchThreshold': 0.1,
    'requireSameDimensions': true
  });
});

module.exports = scenarios;