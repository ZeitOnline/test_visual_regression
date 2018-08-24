const arguments = require( 'minimist' )( process.argv.slice( 2 ) );
const scenarios = require( `./backstop_tests/${arguments.test}.js` );
const beforeScript = `${arguments.before}.js`;
const readyScript = `${arguments.ready}.js`;

module.exports = {
    "id": "",
    "viewports": [
        {
          "label": "phone",
          "width": 320,
          "height": 480
        },
        {
          "label": "tablet",
          "width": 1024,
          "height": 768
        }
      ],
      "onBeforeScript": "puppet/onBefore.js" || beforeScript,
      "onReadyScript": "puppet/onReady.js" || readyScript,
      "scenarios": scenarios,
      "paths": {
        "bitmaps_reference": "backstop_data/bitmaps_reference",
        "bitmaps_test": "backstop_data/bitmaps_test",
        "engine_scripts": "backstop_data/engine_scripts",
        "html_report": "backstop_data/html_report",
        "ci_report": "backstop_data/ci_report"
      },
      "report": ["browser"],
      "engine": "puppeteer",
      "engineOptions": {
          "args": ["--no-sandbox"]
      },
      "asyncCaptureLimit": 5,
      "asyncCompareLimit": 50,
      "debug": false,
      "debugWindow": false
}