let scenarios = []
let testUrls = [
  'http://localhost:9090/zeit-online/parquet-feeds'
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
    'selectors': ['.cp-region--parquet'],
    'selectorExpansion': true,
    'misMatchThreshold': 0.1,
    'requireSameDimensions': true
  })
})

module.exports =
{
  'id': 'podcast-header',
  'viewports': [
    {
      'label': 'phone',
      'width': 320,
      'height': 480
    },
    {
      'label': 'tablet',
      'width': 768,
      'height': 1024
    },
    {
      'label': 'desktop',
      'width': 1280,
      'height': 800
    }
  ],
  'onBeforeScript': '',
  'onReadyScript': '',
  'scenarios': scenarios,
  'paths': {
    'bitmaps_reference': 'backstop_data/bitmaps_reference/parquet-feeds',
    'bitmaps_test': 'backstop_data/bitmaps_test/parquet-feeds',
    'engine_scripts': 'backstop_data/engine_scripts/parquet-feeds',
    'html_report': 'backstop_data/html_report/parquet-feeds',
    'ci_report': 'backstop_data/ci_report/parquet-feeds'
  },
  'report': ['browser'],
  'engine': 'chrome',
  'engineFlags': [],
  'asyncCaptureLimit': 5,
  'asyncCompareLimit': 50,
  'debug': false,
  'debugWindow': false
}
