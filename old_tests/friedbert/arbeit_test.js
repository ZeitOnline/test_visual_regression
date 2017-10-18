/*
  Require and initialise PhantomCSS module
  Paths are relative to CasperJs directory
*/

var urlToFilename = require('../../utils/url_to_filename')
var fs = require('fs')
var path = fs.absolute(fs.workingDirectory + '/phantomcss.js')
var phantomcss = require(path)

casper.test.begin('Friedbert visual tests for vertical ARBEIT', function (test) {
  phantomcss.init({
    rebase: casper.cli.get('rebase'),
    casper: casper,
    libraryRoot: fs.absolute(fs.workingDirectory + ''),
    screenshotRoot: fs.absolute(fs.workingDirectory + '/../screenshots/arbeit'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/../failures/arbeit'),
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
    'http://localhost:9090/arbeit/index',
    'http://localhost:9090/arbeit/article/01-digitale-nomaden',
    'http://localhost:9090/arbeit/article/02-gesundheit-mitarbeiter',
    'http://localhost:9090/arbeit/article/debate',
    'http://localhost:9090/arbeit/article/header-dark',
    'http://localhost:9090/arbeit/article/header-dark-registration?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    'http://localhost:9090/arbeit/article/infografix',
    'http://localhost:9090/arbeit/article/inline-gallery',
    'http://localhost:9090/arbeit/article/jobbox-ticker',
    'http://localhost:9090/arbeit/article/keywords',
    'http://localhost:9090/arbeit/article/marginalia',
    'http://localhost:9090/arbeit/article/paginated',
    'http://localhost:9090/arbeit/article/podcast',
    'http://localhost:9090/arbeit/article/quotes',
    'http://localhost:9090/arbeit/article/simple-long-title',
    'http://localhost:9090/arbeit/article/simple-nextread',
    'http://localhost:9090/arbeit/centerpage/jobbox-dropdown',
    'http://localhost:9090/arbeit/centerpage/jobbox-ticker',
    'http://localhost:9090/arbeit/centerpage/teaser-debate',
    'http://localhost:9090/arbeit/centerpage/teaser-duo',
    'http://localhost:9090/arbeit/centerpage/teaser-lead',
    'http://localhost:9090/arbeit/centerpage/teaser-podcast',
    'http://localhost:9090/arbeit/centerpage/teaser-quote',
    'http://localhost:9090/arbeit/centerpage/teaser-small',
    'http://localhost:9090/arbeit/centerpage/teaser-topic',
    'http://localhost:9090/arbeit/centerpage/teaser-topiccluster',
    'http://localhost:9090/arbeit/centerpage/teaser-to-zplus-abo',
    'http://localhost:9090/arbeit/centerpage/teaser-to-zplus-registration',
    'http://localhost:9090/arbeit/centerpage/thema-opulent',
    'http://localhost:9090/arbeit/centerpage/tube'
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
