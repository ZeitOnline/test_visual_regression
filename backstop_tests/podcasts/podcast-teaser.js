let scenarios = []
let testUrls = [
  'http://localhost:9090/zeit-online/centerpage/podcast-teaser',
  'http://localhost:9090/arbeit/centerpage/teaser-podcast'
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
    'selectors': ['.teaser-podcast'],
    'selectorExpansion': true,
    'misMatchThreshold': 0.1,
    'requireSameDimensions': true
  })
})

module.exports =
{
  'id': 'podcast-teaser',
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
    'bitmaps_reference': 'backstop_data/bitmaps_reference/podcast_teaser',
    'bitmaps_test': 'backstop_data/bitmaps_test/podcast_teaser',
    'engine_scripts': 'backstop_data/engine_scripts/podcast_teaser',
    'html_report': 'backstop_data/html_report/podcast_teaser',
    'ci_report': 'backstop_data/ci_report/podcast_teaser'
  },
  'report': ['browser'],
  'engine': 'chrome',
  'engineFlags': [],
  'asyncCaptureLimit': 5,
  'asyncCompareLimit': 50,
  'debug': false,
  'debugWindow': false
}
