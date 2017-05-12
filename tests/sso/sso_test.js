/*
  Require and initialise PhantomCSS module
  Paths are relative to CasperJs directory
*/

/* global casper , __utils__ */

var urlToFilename = require('../../utils/url_to_filename')
var fs = require('fs')
var pathPhantom = fs.absolute(fs.workingDirectory + '/phantomcss.js')
var phantomcss = require(pathPhantom)
// var server = require('webserver').create()
// var html = fs.read( fs.absolute( fs.workingDirectory + '/demo/coffeemachine.html' ));
//
// server.listen(8080,function(req,res){
//  res.statusCode = 200;
//  res.headers = {
//  'Cache': 'no-cache',
//  'Content-Type': 'text/html;charset=utf-8'
//  };
//  res.write(html);
//  res.close();
// });

casper.test.begin('SSO visual tests', function (test) {
  phantomcss.init({
    rebase: casper.cli.get('rebase'),
  // SlimerJS needs explicit knowledge of this Casper, and lots of absolute paths
    casper: casper,
    libraryRoot: fs.absolute(fs.workingDirectory + ''),
    screenshotRoot: fs.absolute(fs.workingDirectory + '/screenshots/sso'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/failures/sso'),
    addLabelToFailedImage: false
  /*
  screenshotRoot: '/screenshots',
  failedComparisonsRoot: '/failures'
  casper: specific_instance_of_casper,
  libraryRoot: '/phantomcss',
  fileNameGetter: function overide_file_naming(){},
  onPass: function passCallback(){},
  onFail: function failCallback(){},
  onTimeout: function timeoutCallback(){},
  onComplete: function completeCallback(){},
  hideElements: '#thing.selector',
  addLabelToFailedImage: true,
  outputSettings: {
  errorColor: {
  red: 255,
  green: 255,
  blue: 0
  },
  errorType: 'movement',
  transparency: 0.3
  } */
  })

  casper.on('remote.message', function (msg) {
    this.echo(msg)
  })

  casper.on('error', function (err) {
    this.die('PhantomJS has errored: ' + err)
  })

  casper.on('resource.error', function (err) {
    casper.log('Resource load error: ' + err, 'warning')
  })

  /*
  The test scenario
  */

  var links = ['http://localhost:9070/anmelden', 'http://localhost:9070/registrieren']

  casper.start().each(links, function (self, link) {
    // desktop view
    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(1920, 1080).then(function () {
        phantomcss.screenshot('.userform', filename + '_userform')
        phantomcss.screenshot('html', filename + '_fullscreen_desktop')
        casper.then(function provokeFormError () {
          casper.evaluate(function () {
            document.querySelector('form').setAttribute('novalidate', 'true')
          })
          this.fill('form', {
            'email': 'foo',
            'pass': '123456'
          }, true)
          phantomcss.screenshot('.userform', filename + '_userform_error_desktop')
        })
      })
    })

    // mobile view
    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(350, 600).then(function () {
        phantomcss.screenshot('html', filename + '_idle_mobile')
        casper.then(function provokeFormError () {
          casper.evaluate(function () {
            document.querySelector('form').setAttribute('novalidate', 'true')
          })
          this.fill('form', {
            'email': 'foo',
            'pass': '123456'
          }, true)
          phantomcss.screenshot('html', filename + '_input_error_mobile')
        })
      })
    })
  })

  // check loggedin mobile view
  casper.then(function () {
    /*
      eslint camelcase: [2, {properties: "never"}]
    */
    casper.thenOpen('http://localhost:9070/anmelden', function () {
      // make sure to use valid acs credentials
      casper.then(function login () {
        casper.evaluate(function () {
          document.querySelector('form').setAttribute('novalidate', 'true')
        })
        this.fill('form', {
          'email': 'foo@bar.de',
          'pass': '123456'
        }, true)
      })
      // expand mobile menu
      casper.viewport(350, 600).then(function () {
        casper.thenOpen('http://localhost:9070/emailadresseaendern', function () {
          phantomcss.screenshot('html', 'loggedin_changemail_idle_mobile')
          casper.then(function expandMenu () {
            casper.click('.header-nav__icon')
            phantomcss.screenshot('html', 'loggedin_changemail_menu_expanded_mobile')
          })
        })
      })
    })
  })

  // mobile oversized-height
  casper.then(function () {
    casper.viewport(350, 1200).then(function viewMobileOversizedHeight () {
      casper.thenOpen('http://localhost:9070/registrieren', function () {
        phantomcss.screenshot('html', 'register_oversized_height_mobile')
        // iterate over input fields
        // todo: isolate as a function and implement in top-level iteration
        var inputs = casper.evaluate(function () {
          return [].map.call(__utils__.findAll('input:not([type="hidden"])'), function (node) {
            return node.getAttribute('name')
          })
        })
        function captureInputs (element, index, array) {
          phantomcss.screenshot('[name="%1"]'.replace('%1', element), 'input_%1'.replace('%1', element))
        }
        inputs.forEach(captureInputs)
      })
    })
  })

  casper.then(function nowCheckTheScreenshots () {
    // compare screenshots
    phantomcss.compareAll()
  })

  /*
  Casper runs tests
  */
  casper.run(function () {
    console.log('\nTHE END.')
    // phantomcss.getExitStatus() // pass or fail?
    casper.test.done()
  })
})
