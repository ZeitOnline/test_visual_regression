const scenarios = []
const host = 'http://localhost:9090'
const urls = [
  '/zeit-magazin/mode-design/2014-05/karl-lagerfeld-interview',
  '/zeit-magazin/test-cp-legacy/asset-test-1',
  '/zeit-magazin/test-cp-legacy/card-citation',
  '/zeit-magazin/test-cp-legacy/card-flip-flip',
  '/zeit-magazin/test-cp-legacy/card-flip-read',
  '/zeit-magazin/test-cp-legacy/card-flip-read-bildergruppe',
  '/zeit-magazin/test-cp-legacy/card-flip-share',
  '/zeit-magazin/test-cp-legacy/card-picture',
  '/zeit-magazin/test-cp-legacy/card-picture-bildergruppe',
  '/zeit-magazin/test-cp-legacy/card-share-read',
  '/zeit-magazin/test-cp-legacy/card-share-read-bildergruppe',
  '/zeit-magazin/test-cp-legacy/eine-transparente-banane',
  '/zeit-magazin/test-cp-legacy/index',
  '/zeit-magazin/test-cp-legacy/meine-testkarte-bildergruppe',
  '/zeit-magazin/test-cp-legacy/test-cp-large-teaser',
  '/zeit-magazin/test-cp-legacy/test-cp-zmo',
  '/zeit-magazin/test-cp-legacy/test-cp-zmo-2'
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
    selectors: ['document'],
    selectorExpansion: true,
    misMatchThreshold: 0.1,
    requireSameDimensions: true
  })
})

module.exports = scenarios
