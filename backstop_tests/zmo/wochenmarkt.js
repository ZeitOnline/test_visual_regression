const scenarios = []
const host = 'http://localhost:9090'
const urls = [
  '/zeit-magazin/centerpage/wochenmarkt'
]

urls.forEach(url => {
  scenarios.push({
    label: url,
    cookiePath: '',
    url: `${host}${url}`,
    referenceUrl: '',
    readyEvent: '',
    readySelector: '',
    delay: 100,
    hideSelectors: [],
    removeSelectors: [
      '#pDebug'
    ],
    hoverSelector: '',
    clickSelector: '',
    postInteractionWait: '',
    selectors: ['main'],
    selectorExpansion: true,
    misMatchThreshold: 0.1,
    requireSameDimensions: true
  })
})

module.exports = scenarios
