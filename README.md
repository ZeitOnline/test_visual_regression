# Visual Regression Testing with BackstopJS

## General
The visual regression process contains three steps:
- ### reference
  - generate the ideal result (how it should look) in order to compare the test result to this one later on.
- ### test
  - generate the real result (how it actually looks) to compare this one to the reference.
- ### approve
  - when the test is fine and the references shall be updated, you may approve them.

## Prerequisites

#### 1. Install [BackstopJS](https://github.com/garris/BackstopJS)

- Using npm: `npm install -g backstopjs`

#### 2. Clone this repo and install dependencies

1. `git clone git@github.com:ZeitOnline/test_visual_regression.git`
2. `cd test_visual_regression`
3. `npm i`

Resulting in the following directory tree:

```
.
├── backstop_data
│   ├── bitmaps_reference
│   │   └── [...] —> Generated reference screenshots (how it should look like)
│   ├── bitmaps_test
│   │   └── [...] —> Generated screenshots after testing (how it actually looks like)
│   └── html_report
│       └── [...] —> The report generated by BackstopJS after testing
├── backstop_tests
│   └── [...] —> Backstop test files/configs go here
├── old_tests
│   └── [...] —> To be transfered to backstop configs
├── utils
│   └── [...] —> Utility scripts go here
├── README.md
├── backstop-demo.json —> Demo test config generated by backstop
├── package-lock.json
└── package.json
```

#### 3. Make sure your (needed) local servers are running (Friedbert, SSO, ...)

## Running tests


#### 1. If no reference screenshots are available

Generate a reference you want to test against later on. This will create screenshots of all pages/elements that are defined in the config that is passed in as an argument.

`npm run reference`

Example: `npm run reference:zmo`

for further examples take a look at the package.json. Any possible test should be listed there

#### 2. Test against the reference

After making some changes to your code, you might want to test if the pages still look the same or if they have been affected by your changes. After running the following command, a HTML report is generated and opened in your default browser.

`npm run test`

Example: `npm run test:zmo`

#### 3. Approve changes

If you are happy with the results after testing, you may promote the test screenshots to be the new reference screenshots.

`npm run approve`

Example: `npm run approve:zmo`

## Creating tests

Test configs for BackstopJS can be setup using JSON files or JS modules, see [BackstopJS Docs](https://github.com/garris/BackstopJS).

## Further reading
- [BackstopJS ReadMe](https://github.com/garris/BackstopJS)
