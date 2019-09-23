const scenarios = []
const host = 'http://localhost:9090'
const urls = [
  '/zeit-magazin/article/01',
  '/zeit-magazin/article/02',
  '/zeit-magazin/article/03',
  '/zeit-magazin/article/03a',
  '/zeit-magazin/article/04',
  '/zeit-magazin/article/05',
  '/zeit-magazin/article/06',
  '/zeit-magazin/article/07',
  '/zeit-magazin/article/08',
  '/zeit-magazin/article/09',
  '/zeit-magazin/article/10',
  '/zeit-magazin/article/abo-briefmarke',
  '/zeit-magazin/article/abo-column',
  '/zeit-magazin/article/abo-default',
  '/zeit-magazin/article/abo-leinwand',
  '/zeit-magazin/article/abo-mode',
  '/zeit-magazin/article/abo-traum',
  '/zeit-magazin/article/advertorial',
  '/zeit-magazin/article/advertorial-onepage',
  '/zeit-magazin/article/all-blocks',
  '/zeit-magazin/article/article_video_asset',
  '/zeit-magazin/article/article_video_asset_list',
  '/zeit-magazin/article/artikel-mit-fiktiven-assets',
  '/zeit-magazin/article/artikel-mit-unvollstaendigen-assets',
  '/zeit-magazin/article/artikel-ohne-assets',
  '/zeit-magazin/article/authorbox',
  '/zeit-magazin/article/autorenbox',
  '/zeit-magazin/article/cluster-beispiel',
  '/zeit-magazin/article/essen-geniessen-spargel-lamm',
  '/zeit-magazin/article/gesellschaftskritik-grumpy-cat',
  '/zeit-magazin/article/header-briefmarke',
  '/zeit-magazin/article/header-column',
  '/zeit-magazin/article/header-default',
  '/zeit-magazin/article/header-leinwand',
  '/zeit-magazin/article/header-mode',
  '/zeit-magazin/article/header-text-only',
  '/zeit-magazin/article/header-traum',
  '/zeit-magazin/article/header_video',
  '/zeit-magazin/article/infografix',
  '/zeit-magazin/article/infographic',
  '/zeit-magazin/article/inline-gallery',
  '/zeit-magazin/article/inline-imagegroup',
  '/zeit-magazin/article/jquery-local-scope',
  '/zeit-magazin/article/kochen-wuerzen-veganer-kuchen',
  '/zeit-magazin/article/liebeskolumne-rationalitaet-emotionen',
  '/zeit-magazin/article/martenstein-portraitformat',
  '/zeit-magazin/article/martenstein-squareformat',
  '/zeit-magazin/article/martenstein-transparenz-test',
  '/zeit-magazin/article/martenstein-wideformat',
  '/zeit-magazin/article/nobanner',
  '/zeit-magazin/article/standardkolumne-beispiel',
  '/zeit-magazin/article/standardkolumne-ohne-bild-beispiel',
  '/zeit-magazin/article/vegetarisch-kochen-fuer-gaeste',
  '/zeit-magazin/article/video',
  '/zeit-magazin/article/volumeteaser',
  '/zeit-magazin/article/zplus-zmo-paid',
  '/zeit-magazin/article/zplus-zmo-register'
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
