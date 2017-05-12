/*
  Require and initialise PhantomCSS module
  Paths are relative to CasperJs directory
*/
var urlToFilename = require('../../utils/url_to_filename')
var fs = require('fs')
var path = fs.absolute(fs.workingDirectory + '/phantomcss.js')
var phantomcss = require(path)

casper.test.begin('Friedbert visual tests', function (test) {
  phantomcss.init({
    rebase: casper.cli.get('rebase'),
    // SlimerJS needs explicit knowledge of this Casper, and lots of absolute paths
    casper: casper,
    libraryRoot: fs.absolute(fs.workingDirectory + ''),
    screenshotRoot: fs.absolute(fs.workingDirectory + '/screenshots/FEM-54'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/failures/FEM-54'),
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
    'http://localhost:9090/zeit-online/article/simple-nextread',
    'http://localhost:9090/zeit-online/article/simple-verlagsnextread',
    'http://localhost:9090/zeit-online/article/inline-gallery',
    'http://localhost:9090/zeit-online/gallery/biga_1',
    'http://localhost:9090/zeit-online/video/3537342483001',
    'http://localhost:9090/zeit-online/article/all-blocks',
    'http://localhost:9090/zeit-online/article/angebot',
    'http://localhost:9090/framebuilder?adlabel=sch%C3%B6nes%20Wurstbrot',
    'http://localhost:9090/zeit-online/article/infografix'
  ]

  casper.start()

  casper.thenOpen('http://localhost:9070/anmelden', function () {
    casper.then(function login () {
      this.fill('form', {
        'email': 'foo@bar.de',
        'pass': '123456'
      }, true)
    })
  })

  casper.each(links, function (self, link) {
    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(1920, 1080).then(function () {
        phantomcss.screenshot('main', filename + '_main_desktop')
      })
    })

    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(360, 600).then(function () {
        phantomcss.screenshot('main', filename + '_main_mobile')
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
