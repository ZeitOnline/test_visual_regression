const glob = require('glob');
const pattern = './scenarios/**/*.js';
const configFiles = glob.sync(pattern);
const viewports = [
  { label: 'mobile', width: 320, height: 480 },
  { label: 'tablet', width: 768, height: 1024 },
  { label: 'desktop', width: 1024, height: 768 },
];

const scenarios = configFiles.reduce((accumulator, filename) => {
  const thisConfig = require(filename);
  const labelPrefix = filename.split('/').slice(2).join('::').slice(0, -3);

  thisConfig.forEach(scenario => {
    scenario.label = [labelPrefix, scenario.url, scenario.label].join(' ').trimEnd();
    if (scenario.viewports) {
      scenario.viewports = viewports.filter(({ label }) => scenario.viewports.includes(label));
    }
  });

  return accumulator.concat(thisConfig);
}, []);

function mergeDefaults(scenario) {
  const defaults = {
    removeSelectors: ['#pDebug'],
    selectors: ['main'],
  };

  scenario.url = 'http://localhost:9090/' + scenario.url;

  return Object.assign({}, defaults, scenario);
}

module.exports = {
  id: '',
  viewports: viewports,
  onBeforeScript: false,
  onReadyScript: false,
  scenarios: scenarios.map(mergeDefaults),
  // scenarios: [],
  paths: {
    bitmaps_reference: 'data/references',
    bitmaps_test: 'data/tests',
    engine_scripts: 'backstop_data/engine_scripts',
    html_report: 'backstop_data/html_report',
    ci_report: 'backstop_data/ci_report',
  },
  report: ['browser'],
  engine: 'puppeteer',
  engineOptions: {
    args: ['--no-sandbox'],
  },
  asyncCaptureLimit: 2,
  asyncCompareLimit: 50,
  debug: false,
  debugWindow: false,
};
