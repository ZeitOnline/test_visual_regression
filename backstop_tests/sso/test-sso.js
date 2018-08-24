let scenarios = []
const urls = [
  'http://localhost:9070/emailadresseaendern',
  'http://localhost:9070/registrieren',
  'http://localhost:9070/anmelden',
  'http://localhost:9070/opt-out'
]

urls.forEach( url => {
  scenarios.push({
    'label': url.replace('http://localhost:9070/', '').replace(/\//g, '_'),
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
  })
})

module.exports = scenarios;