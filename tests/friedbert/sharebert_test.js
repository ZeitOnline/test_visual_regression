/*
  Require and initialise PhantomCSS module
  Paths are relative to CasperJs directory
*/

var urlToFilename = require('../../utils/url_to_filename')
var fs = require('fs')
var path = fs.absolute(fs.workingDirectory + '/phantomcss.js')
var phantomcss = require(path)

casper.test.begin('Friedbert visual tests for live Sharebert Twitter-Quote', function (test) {
  phantomcss.init({
    rebase: casper.cli.get('rebase'),
    casper: casper,
    libraryRoot: fs.absolute(fs.workingDirectory + ''),
    screenshotRoot: fs.absolute(fs.workingDirectory + '/../screenshots/sharebert'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/../failures/sharebert'),
    addLabelToFailedImage: false
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

  var links = [
    'http://live0.zeit.de/twitter-quote/?quote=Das%20hat%20alles%20keinen%20Gin'
  ]

    // wait einführen fürs Laden der Bilder.

  casper.start().each(links, function (self, link) {
    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(1920, 1080).then(function () {
        this.wait(1000, function () {
          phantomcss.screenshot('body', filename + '_fullscreen_desktop')
        })
      })
    })

    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(360, 600).then(function () {
        this.wait(1000, function () {
          phantomcss.screenshot('body', filename + '_fullscreen_mobile')
        })
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
