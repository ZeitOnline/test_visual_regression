let scenarios = []
let testUrls = [
  'http://localhost:9090/arbeit/index',
  'http://localhost:9090/arbeit/article/01-digitale-nomaden',
  'http://localhost:9090/arbeit/article/02-gesundheit-mitarbeiter',
  'http://localhost:9090/arbeit/article/debate',
  'http://localhost:9090/arbeit/article/header-dark',
  'http://localhost:9090/arbeit/article/header-dark-registration?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
  'http://localhost:9090/arbeit/article/infografix',
  'http://localhost:9090/arbeit/article/inline-gallery',
  'http://localhost:9090/arbeit/article/jobbox-ticker',
  'http://localhost:9090/arbeit/article/keywords',
  'http://localhost:9090/arbeit/article/marginalia',
  'http://localhost:9090/arbeit/article/paginated',
  'http://localhost:9090/arbeit/article/podcast',
  'http://localhost:9090/arbeit/article/quotes',
  'http://localhost:9090/arbeit/article/sharequote',
  'http://localhost:9090/arbeit/article/simple-long-title',
  'http://localhost:9090/arbeit/article/simple-nextread',
  'http://localhost:9090/arbeit/centerpage/jobbox-dropdown',
  'http://localhost:9090/arbeit/centerpage/jobbox-ticker',
  'http://localhost:9090/arbeit/centerpage/teaser-debate',
  'http://localhost:9090/arbeit/centerpage/teaser-duo',
  'http://localhost:9090/arbeit/centerpage/teaser-lead',
  'http://localhost:9090/arbeit/centerpage/teaser-podcast',
  'http://localhost:9090/arbeit/centerpage/teaser-quote',
  'http://localhost:9090/arbeit/centerpage/teaser-small',
  'http://localhost:9090/arbeit/centerpage/teaser-topic',
  'http://localhost:9090/arbeit/centerpage/teaser-topiccluster',
  'http://localhost:9090/arbeit/centerpage/teaser-to-zplus-abo',
  'http://localhost:9090/arbeit/centerpage/teaser-to-zplus-registration',
  'http://localhost:9090/arbeit/centerpage/thema-opulent',
  'http://localhost:9090/arbeit/centerpage/tube'
]

testUrls.forEach(url => {
  scenarios.push({
    'label': url.replace('http://localhost:9090/', '').replace(/\//g, '_'),
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

module.exports =
{
  'id': 'test_zar',
  'viewports': [
    {
      'label': 'phone',
      'width': 320,
      'height': 480
    },
    {
      'label': 'tablet',
      'width': 1024,
      'height': 768
    }
  ],
  'onBeforeScript': '',
  'onReadyScript': '',
  'scenarios': scenarios,
  'paths': {
    'bitmaps_reference': 'backstop_data/bitmaps_reference',
    'bitmaps_test': 'backstop_data/bitmaps_test',
    'engine_scripts': 'backstop_data/engine_scripts',
    'html_report': 'backstop_data/html_report',
    'ci_report': 'backstop_data/ci_report'
  },
  'report': ['browser'],
  'engine': 'chrome',
  'engineFlags': [],
  'asyncCaptureLimit': 5,
  'asyncCompareLimit': 50,
  'debug': false,
  'debugWindow': false
}
