# Testing visual Regression using [PhantomCSS](https://github.com/Huddle/PhantomCSS#getting-started-try-the-demo)

## Prerequisites

#### 1. Install [CasperJS](http://docs.casperjs.org/en/latest/installation.html)

- homebrew: `brew install casperjs`

#### 2. Clone this repo and install dependencies

`git clone git@github.com:ZeitOnline/test_visual_regression.git && cd test_visual_regression && npm install && cd PhantomCSS && git submodule init && git submodule update && npm install`

Resulting in the following directory tree:

```
test_visual_regression
│   .eslintrc
│   .gitignore
│   .gitmodules
│   package.json
│   README.md
│
└───PhantomCSS
│   │   [screenshots will appear here]
│   │   [failures will appear here]
│   │   ...
│
└───tests
│    │
│    └───friedbert
│    │   │   friedbert_test.js
│    │   │   ...
│    │
│    └───sso
│        │   sso_test.js
│        │   ...
│
...
```
#### 3. Have your local server (friedbert, SSO, ...) running

## Running tests

#### Tests need to be run from  the PhantomCSS directory

```
cd PhantomCSS
casperjs test ../tests/sso/sso_test.js
```

If you run a particular test for the first you'll be notified by a console output that you've just created a new baseline of screenshots.

Now run the tests a second time in whatever checked out state of your application you want to verify against the previously established baseline. A new set of screenshots with the suffix `.diff` is put into the specified output directory and compared against the baseline of screenshots (if none is found, a new one will be created).

Output directiries are specified in the tests themselves like:

```
screenshotRoot: fs.absolute(fs.workingDirectory + '/screenshots/sso'),
failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/failures/sso')
```

#### Failing example test

```
...
│
└───PhantomCSS
│   │
│   └───screenshots
│   │   │
│   │   └───sso
│   │       │   anmelden.png [baseline]
│   │       │   anmelden.diff.png [the actual state]
│   │       │   anmelden.fail.png [diff between the above]
│   │       │   ...
│   │
│   └───failures
│   │   │
│   │   └───sso
│   │       │   anmelden.fail.png
│   │       │   ...
│   │
│   ...
...
```

## Further reading
- [CasperJS Docs](http://docs.casperjs.org/en/latest/) (scripting user interaction)
- [ PhantomJS API](http://phantomjs.org/api/)
