# Visual Regression Testing with [BackstopJS](https://github.com/garris/BackstopJS)

## General
The visual regression process contains three steps:
- ### reference
  - generate the ideal result (how it should look) in order to compare the test result to this one later on.
- ### test
  - generate the real result (how it actually looks) to compare this one to the reference.
- ### approve
  - when the test is fine and the references shall be updated, you may approve them.

## Prerequisites

#### 1. Clone this repo and install dependencies

1. `git clone git@github.com:ZeitOnline/test_visual_regression.git`
2. `cd test_visual_regression`
3. `npm i`

Resulting in the following directory tree:

```
.
├── backstop_data
│   └── html_report
│       └── [...] —> The report generated by BackstopJS after testing
├── backstop_tests
│   └── [...] —> Legacy Backstop test files
├── data
│   ├── references
│   │   └── [...] —> Generated reference screenshots (how it should look like)
│   ├── tests
│   └── [...] —> Generated screenshots after testing (how it actually looks like)
├── engine_scripts
│   └── [...] -> scripts for engine (e.g. puppeteer) control
├── scenarios
│   └── [...] —> Backstop test scenarios
├── utils
│   └── [...] —> Utility scripts go here
├── README.md
├── backstop-demo.json —> Demo test config generated by backstop
├── package-lock.json
└── package.json
```

#### 2. Make sure your (needed) local servers are running (Friedbert, SSO, ...)

## Running tests


#### 1. If no reference screenshots are available

Generate a reference you want to test against later on. This will create screenshots of all pages/elements, optionally filtered by label. Pass a ``--filter=<scenarioLabelRegex>`` argument to just run scenarios matching your scenario label.

`npm run reference`

Example: `npm run reference -- --filter=zon::video`

For further examples take a look at the package.json.

#### 2. Test against the reference

After making some changes to your code, you might want to test if the pages still look the same or if they have been affected by your changes. After running the following command, a HTML report is generated and opened in your default browser.

`npm run test`

Example: `npm run test -- --filter=zmo::`

#### 3. Approve changes

If you are happy with the results after testing, you may promote the test screenshots to be the new reference screenshots.

`npm run approve`

Example: `npm run approve -- --filter=zon-teaser-podcast-lead`

## Creating tests

Test configs for BackstopJS can be setup using JSON files or JS modules, see [BackstopJS Docs](https://github.com/garris/BackstopJS).

### Creating test scenarios for dark mode

To generate test scenarios testing the dark theme, you can add an engine script to your test scenario as an `onBeforeScript` property. To prevent duplicate testing, it is required that you also add the `label` of `darkmode` to the scenario. For example:

```js
{
  label: 'darkmode',
  onBeforeScript: 'prefers-color-scheme-dark.js',
  url: '/zeit-online/article/simple',
  readySelector: '.nav__ressorts--fitted',
  selectors: ['header.header'],
  viewports: ['tablet', 'desktop'],
  },
```

### Run all given test scenarios in darkmode
By toggling `enhanceWithDarkMode` in `backstop-settings.js` to `true` (default: `true`), you can switch on/off the duplication of all tests for darkmode. If switched on however, manually added darkmode szenarion like the one above are omitted to avoid duplication.

If you want to run darkmode tests seperately use the `darkmode` key word as filter, e.g.

```sh
npm run reference -- --filter=darkmode
```

### Creating tests for hover effects
The requirements to make working screenshots of hover effects are a bit challenging and poorly documented. To make this work the engine script `clickAndHoverHelper.js` needs to be used as an `onReadyScript`, which we do by default in the global `onReady.js`. Additionally the shot cannot be made by selecting a dom node on the page rather the `selectors` property needs to be set to `document`. For example:

```js
{
  url: '/zeit-online/centerpage/zon-teaser-lead',
  hoverSelectors: ['.zon-teaser-leadtopiclink'],
  selectors: ['document'],
},
```

### Screenshotting click events
Testing for click events also need the engine script `clickAndHoverHelper.js` (supplied by default configuration). You can configure a test with a given list of `clickSelectors`. The trick here is to chose the correct `selector` to see the resulting action on the screenshot. For instance a click on a bookmark icon (if the user is not logged in) will result in a dialog in the middle of the viewport thus using `selectors: ['viewport']` is mandatory to _see_ the result. E.g.:

```js
{
  url: '/zeit-online/centerpage/zon-teaser-standard',
  clickSelectors: ['.bookmark-icon'],
  selectors: ['viewport'],
},
```

## Further reading
- [BackstopJS ReadMe](https://github.com/garris/BackstopJS)
