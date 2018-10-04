let scenarios = [];
const urls = [
    'http://localhost:9090/index',
    'http://localhost:9090/amp/campus/article/common',
    'http://localhost:9090/arbeit/centerpage/advertorial',
    'http://localhost:9090/zeit-online/storystream/articles/syriza-tsipras-parlamentswahl',
    'http://localhost:9090/zeit-online/storystream-teaser',
    'http://localhost:9090/zeit-online/storystream/dummy',
    'http://localhost:9090/zeit-online/article/01',
    'http://localhost:9090/zeit-online/author-teaser',
    'http://localhost:9090/zeit-online/teaser-gallery-setup',
    'http://localhost:9090/campus/centerpage/advertorial',
    'http://localhost:9090/campus/article/flexible-toc',
    'http://localhost:9090/zeit-online/dossier-teaser',
    'http://localhost:9090/zeit-magazin/teaser-square-large',
    'http://localhost:9090/zeit-magazin/index'
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