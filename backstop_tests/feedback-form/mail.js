let scenarios = []
let testUrls = [
  'http://localhost:9090/autoren/S/Thomas_Strothjohann/index/feedback',
  'http://localhost:9090/zeit-online/article/feedback'
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
  'id': 'test_author_feedback',
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
    'bitmaps_reference': 'backstop_data/feedback-form/bitmaps_reference',
    'bitmaps_test': 'backstop_data/feedback-form/bitmaps_test',
    'engine_scripts': 'backstop_data/feedback-form/engine_scripts',
    'html_report': 'backstop_data/feedback-form/html_report',
    'ci_report': 'backstop_data/feedback-form/ci_report'
  },
  'report': ['browser'],
  'engine': 'chrome',
  'engineFlags': [],
  'asyncCaptureLimit': 5,
  'asyncCompareLimit': 50,
  'debug': false,
  'debugWindow': false
}
