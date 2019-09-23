const scenarios = []
const urls = [
  'http://localhost:9090/campus/article/common?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
  'http://localhost:9090/campus/article/common?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
  'http://localhost:9090/campus/article/common?C1-Meter-Status=always_paid'
]

urls.forEach(url => {
  scenarios.push({
    label: url.replace('http://localhost:9090/', '').replace(/\//g, '_'),
    cookiePath: '',
    url: url,
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
    selectors: [],
    selectorExpansion: true,
    misMatchThreshold: 0.1,
    requireSameDimensions: true
  })
})

module.exports = scenarios
