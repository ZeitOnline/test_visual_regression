let scenarios = []
let testUrls = [
  'http://localhost:9070/emailadresseaendern',
  'http://localhost:9070/registrieren',
  'http://localhost:9070/anmelden',
  'http://localhost:9070/opt-out'
]

testUrls.forEach(url => {
  scenarios.push({
    'label': url.replace('http://localhost:9070/', '').replace(/\//g, '_'),
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
  'id': 'test_sso',
  'viewports': [
    {
      'label': 'phone',
      'width': 320,
      'height': 568
    },
    {
      'label': 'tablet-landscape',
      'width': 1024,
      'height': 768
    }
  ],
  'onBeforeScript': '',
  'onReadyScript': 'interactions',
  'scenarios': scenarios,
  'paths': {
    'bitmaps_reference': 'backstop_data/sso/test-sso-interaction/bitmaps_reference',
    'bitmaps_test': 'backstop_data/sso/test-sso-interaction/bitmaps_test',
    'engine_scripts': 'backstop_tests/sso/ui-scripts',
    'html_report': 'backstop_data/sso/test-sso-interaction/html_report',
    'ci_report': 'backstop_data/sso/test-sso-interaction/ci_report'
  },
  'report': ['browser'],
  'engine': 'casper',
  'engineFlags': [],
  'asyncCaptureLimit': 5,
  'asyncCompareLimit': 50,
  'debug': false,
  'debugWindow': false
}
