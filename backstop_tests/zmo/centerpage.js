const scenarios = []
const host = 'http://localhost:9090'
const urls = [
  '/zeit-magazin/centerpage/advertorial',
  '/zeit-magazin/centerpage/article_gallery_asset',
  '/zeit-magazin/centerpage/article_image_asset',
  '/zeit-magazin/centerpage/article_with_broken_image_asset',
  '/zeit-magazin/centerpage/automatic',
  '/zeit-magazin/centerpage/cp_without_assets',
  '/zeit-magazin/centerpage/follow-us',
  '/zeit-magazin/centerpage/index',
  '/zeit-magazin/centerpage/index-without-ads',
  '/zeit-magazin/centerpage/lebensart',
  '/zeit-magazin/centerpage/lebensart-2',
  '/zeit-magazin/centerpage/teasers-to-series',
  '/zeit-magazin/centerpage/tube',
  '/zeit-magazin/centerpage/zmo_zon_matching',
  '/zeit-magazin/centerpage/zplus'
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
