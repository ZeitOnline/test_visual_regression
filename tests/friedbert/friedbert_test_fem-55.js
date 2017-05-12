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
    screenshotRoot: fs.absolute(fs.workingDirectory + '/screenshots/FEM-55'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/failures/FEM-55'),
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

  // var links = [
  //   'http://localhost:9090/konto',
  //   'http://localhost:9090/2017/index',
  //   'http://localhost:9090/2017/14/index',
  //   'http://localhost:9090/suche/index',
  //   'http://localhost:9090/thema/jurastudium',
  //   'http://localhost:9090/autoren/W/Jochen_Wegner/index'
  // ]

  var links = [
    'http://localhost:9090/zeit-online/index',
    'http://localhost:9090/zeit-online/buzz-box',
    'http://localhost:9090/zeit-online/video-stage',
    'http://localhost:9090/zeit-online/centerpage/exclusive',
    'http://localhost:9090/zeit-online/journalistic-formats',
    'http://localhost:9090/2016/index',
    'http://localhost:9090/2016/01/index',
    'http://localhost:9090/konto',
    'http://localhost:9090/suche/index',
    'http://localhost:9090/thema/jurastudium',
    'http://localhost:9090/thema/test',
    'http://localhost:9090/autoren/j_random'
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
        phantomcss.screenshot('main', filename + '_fullscreen_desktop')
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
