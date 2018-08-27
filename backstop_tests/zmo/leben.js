let scenarios = [];
const host = 'http://localhost:9090';
const urls = [
  '/zeit-magazin/leben/2014-05/Martenstein-Online-Kommentare',
  '/zeit-magazin/leben/2014-06/apple-os-x-yosemite',
  '/zeit-magazin/leben/2014-06/apple-os-x-yosemite',
  '/zeit-magazin/leben/2015-02/magdalena-ruecken-fs',
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
      '#pDebug'
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