let scenarios = []
let testUrls = [
  'http://localhost:9090/arbeit/index',
  'http://localhost:9090/arbeit/article/01-digitale-nomaden',
  'http://localhost:9090/arbeit/article/02-gesundheit-mitarbeiter'
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
