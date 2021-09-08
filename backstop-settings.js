const glob = require('glob');
const pattern = './scenarios/**/*.js';
const configFiles = glob.sync(pattern);
const viewports = [
  { label: 'mobile', width: 320, height: 480 },
  { label: 'tablet', width: 768, height: 1024 },
  { label: 'desktop', width: 1024, height: 768 },
];
const darkModeScenarios = [];
const enhanceWithDarkMode = true;

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
    readyTimeout: 8000, // Timeout for readyEvent and readySelector (default: 60000ms)
    removeSelectors: ['#pDebug', '.sticky-nav'],
    selectors: ['main'],
  };

  scenario.url = 'http://localhost:9090/' + scenario.url;

  return Object.assign({}, defaults, scenario);
}

if (enhanceWithDarkMode) {
  scenarios.forEach(scenario => {
    if (scenario.label.indexOf('darkmode') === -1) {
        // needs deep copy of scenario
        const darkScenario = Object.assign({}, scenario);
        darkScenario.label += ' darkmode';
        darkScenario.onBeforeScript = 'prefers-color-scheme-dark.js';
        darkModeScenarios.push(darkScenario);
    }
  });
}

module.exports = {
  id: '',
  viewports: viewports,
  onBeforeScript: false,
  onReadyScript: "puppet/onReady.js",
  scenarios: [...scenarios, ...darkModeScenarios].map(mergeDefaults),
  paths: {
    bitmaps_reference: 'data/references',
    bitmaps_test: 'data/tests',
    engine_scripts: 'engine_scripts',
    html_report: 'data/html_report',
    ci_report: 'data/ci_report',
  },
  report: ['browser'],
  engine: 'puppeteer',
  engineOptions: {
    args: ['--no-sandbox'],
  },
  asyncCaptureLimit: 1, // default: 10
  asyncCompareLimit: 50, // default: 50
  debug: false,
  debugWindow: false,
};
