const scenarios = []
const urls = [
    'http://localhost:9090/zeit-online/hp-rebrush-2019/kpi',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-classic',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-classic-video',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-column',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-gallery',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-gallery-variants',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-lead',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-panorama',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-podcast',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-podcast-lead',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-podcast-variants',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-poster',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-poster-video',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-square-author',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-standard',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-upright',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-video',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/zon-teaser-wide',
    'http://localhost:9090/zeit-online/hp-rebrush-2019/teaser-to-wochenmarkt'
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
