const scenarios = []
const urls = [
  // cp content
  'http://localhost:9090/zeit-online/cp-content/article-01',
  'http://localhost:9090/zeit-online/cp-content/article-02',
  'http://localhost:9090/zeit-online/cp-content/article-03',
  'http://localhost:9090/zeit-online/cp-content/article-05',
  'http://localhost:9090/zeit-online/cp-content/article-06',
  'http://localhost:9090/zeit-online/cp-content/article-ohne-bild',
  'http://localhost:9090/zeit-online/cp-content/kolumne',
  'http://localhost:9090/zeit-online/cp-content/kolumne-julia-zange',
  'http://localhost:9090/zeit-online/cp-content/article-ohne-autorenbild',
  'http://localhost:9090/zeit-online/cp-content/link-teaser',
  'http://localhost:9090/zeit-online/cp-content/liveblog-live',
  'http://localhost:9090/zeit-online/cp-content/liveblog-offline',
  'http://localhost:9090/zeit-online/cp-content/serie_app_kritik',
  // author images
  'http://localhost:9090/zeit-online/cp-content/author_images/Julia_Zange/zon-column',
  // register
  'http://localhost:9090/zeit-online/cp-content/register/article-campus-register',
  'http://localhost:9090/zeit-online/cp-content/register/article-zeit-register',
  'http://localhost:9090/zeit-online/cp-content/register/article-zmo-register',
  'http://localhost:9090/zeit-online/cp-content/register/column-zeit-register',
  'http://localhost:9090/zeit-online/cp-content/register/column-zmo-register',
  'http://localhost:9090/zeit-online/cp-content/register/serie-zon-register',
  'http://localhost:9090/zeit-online/cp-content/register/zon-dossier-register',
  // taglogo
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-campus-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-campus-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-zett-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-zett-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-zm-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-zm-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-zplus-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/article-zplus-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/blog-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/blog-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/column-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/column-d18-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/link-d17-tag',
  'http://localhost:9090/zeit-online/cp-content/taglogo/link-d18-tag'
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
