const scenarios = []
const urls = [
  'http://localhost:9090/index',
  'http://localhost:9090/zeit-online/advertorial-index',
  'http://localhost:9090/zeit-online/author-teaser',
  'http://localhost:9090/zeit-online/basic-teasers-setup',
  'http://localhost:9090/zeit-online/check_teaser_comment_count',
  'http://localhost:9090/zeit-online/classic-teaser',
  'http://localhost:9090/zeit-online/dossier-teaser',
  'http://localhost:9090/zeit-online/fullwidth-teaser',
  'http://localhost:9090/zeit-online/index',
  'http://localhost:9090/zeit-online/index-follow-us',
  'http://localhost:9090/zeit-online/index-with-image',
  'http://localhost:9090/zeit-online/index-with-quizzez',
  'http://localhost:9090/zeit-online/index-with-raw-on-top',
  'http://localhost:9090/zeit-online/invisible-teaser',
  'http://localhost:9090/zeit-online/jobbox',
  'http://localhost:9090/zeit-online/journalistic-formats',
  'http://localhost:9090/zeit-online/journalistic-formats-liveblog',
  'http://localhost:9090/zeit-online/journalistic-formats-zett',
  'http://localhost:9090/zeit-online/large-teaser',
  'http://localhost:9090/zeit-online/link-object',
  'http://localhost:9090/zeit-online/main-teaser-setup',
  'http://localhost:9090/zeit-online/mobile-visible-index',
  'http://localhost:9090/zeit-online/news-teaser',
  'http://localhost:9090/zeit-online/overview',
  'http://localhost:9090/zeit-online/parquet',
  'http://localhost:9090/zeit-online/parquet-teaser-setup',
  'http://localhost:9090/zeit-online/partnerbox-jobs',
  'http://localhost:9090/zeit-online/partnerbox-reisen',
  'http://localhost:9090/zeit-online/printbox',
  'http://localhost:9090/zeit-online/raw_code',
  'http://localhost:9090/zeit-online/slenderized-index',
  'http://localhost:9090/zeit-online/slenderized-index-with-newsbox',
  'http://localhost:9090/zeit-online/storystream-teaser',
  'http://localhost:9090/zeit-online/studiumbox',
  'http://localhost:9090/zeit-online/teaser-broken-setup',
  'http://localhost:9090/zeit-online/teaser-columns-without-authorimage',
  'http://localhost:9090/zeit-online/teaser-gallery-setup',
  'http://localhost:9090/zeit-online/teaser-inhouse-setup',
  'http://localhost:9090/zeit-online/teaser-serie-setup',
  'http://localhost:9090/zeit-online/teaser-shop',
  'http://localhost:9090/zeit-online/teaser-square-setup',
  'http://localhost:9090/zeit-online/thema',
  'http://localhost:9090/zeit-online/topic-teaser',
  'http://localhost:9090/zeit-online/transparent-teaserimage',
  'http://localhost:9090/zeit-online/vertical-spaces',
  'http://localhost:9090/zeit-online/video-stage',
  'http://localhost:9090/zeit-online/video-stage-wo-ads',
  'http://localhost:9090/zeit-online/video-teaser',
  'http://localhost:9090/zeit-online/teaser-broken-setup',
  'http://localhost:9090/zeit-online/webtrekk-test-setup',
  'http://localhost:9090/zeit-online/zeitonline',
  'http://localhost:9090/zeit-online/zett-banner',

  // Beispielautor
  'http://localhost:9090/autoren/S/Thomas_Strothjohann/index'
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
    selectors: ['html'],
    selectorExpansion: true,
    misMatchThreshold: 0.1,
    requireSameDimensions: true
  })
})

module.exports = scenarios
