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
          "width": 768,
          "height": 1024
        },
        {
          "label": "desktop",
          "width": 1024,
          "height": 768
        }
    ],
    "onBeforeScript": false,
    "onReadyScript": false,
    "scenarios": scenarios,
    "paths": {
      "bitmaps_reference": "data/references",
      "bitmaps_test": "data/tests",
      "engine_scripts": "backstop_data/engine_scripts",
      "html_report": "backstop_data/html_report",
      "ci_report": "backstop_data/ci_report"
    },
    "report": ["browser"],
    "engine": "puppeteer",
    "engineOptions": {
        "args": ["--no-sandbox"]
    },
    "asyncCaptureLimit": 2,
    "asyncCompareLimit": 50,
    "debug": false,
    "debugWindow": false
}
