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
    casper: casper,
    libraryRoot: fs.absolute(fs.workingDirectory + ''),
    screenshotRoot: fs.absolute(fs.workingDirectory + '/screenshots/overview'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/failures/overview'),
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
    'http://localhost:9090/campus/article/01-countdown-studium',
    'http://localhost:9090/campus/article/03-spartipps',
    'http://localhost:9090/campus/article/all-blocks',
    'http://localhost:9090/campus/article/authorbox',
    'http://localhost:9090/campus/article/column',
    'http://localhost:9090/campus/article/debate',
    'http://localhost:9090/campus/article/embed-header-image',
    'http://localhost:9090/campus/article/infographic',
    'http://localhost:9090/campus/article/simple-with-nextread-leaserartikel',
    'http://localhost:9090/campus/article/stoa',
    'http://localhost:9090/campus/centerpage/cp-of-cps',
    'http://localhost:9090/campus/centerpage/teaser-graphical',
    'http://localhost:9090/campus/centerpage/teaser-topic',
    'http://localhost:9090/campus/centerpage/teasers',
    'http://localhost:9090/campus/centerpage/thema',
    'http://localhost:9090/campus/index',
    'http://localhost:9090/index',
    'http://localhost:9090/zeit-magazin/article/01',
    'http://localhost:9090/zeit-magazin/article/08',
    'http://localhost:9090/zeit-magazin/article/abo-mode',
    'http://localhost:9090/zeit-magazin/article/advertorial',
    'http://localhost:9090/zeit-magazin/article/all-blocks',
    'http://localhost:9090/zeit-magazin/article/cluster-beispiel',
    'http://localhost:9090/zeit-magazin/article/header-column',
    'http://localhost:9090/zeit-magazin/article/kochen-wuerzen-veganer-kuchen',
    'http://localhost:9090/zeit-magazin/article/martenstein-transparenz-test',
    'http://localhost:9090/zeit-magazin/article/standardkolumne-beispiel',
    'http://localhost:9090/zeit-magazin/article/volumeteaser',
    'http://localhost:9090/zeit-magazin/buzz',
    'http://localhost:9090/zeit-magazin/centerpage/index',
    'http://localhost:9090/zeit-magazin/centerpage/lebensart',
    'http://localhost:9090/zeit-magazin/centerpage/zplus',
    'http://localhost:9090/zeit-magazin/teaser-card',
    'http://localhost:9090/zeit-magazin/teaser-landscape-small',
    'http://localhost:9090/zeit-magazin/teaser-upright',
    'http://localhost:9090/zeit-online/article/embed-header-image',
    'http://localhost:9090/zeit-online/article/fischer',
    'http://localhost:9090/zeit-online/article/infographic',
    'http://localhost:9090/zeit-online/article/inline-gallery',
    'http://localhost:9090/zeit-online/article/simple-nextread',
    'http://localhost:9090/zeit-online/article/simple-nextread-zett',
    'http://localhost:9090/zeit-online/article/tags',
    'http://localhost:9090/zeit-online/article/volumeteaser',
    'http://localhost:9090/zeit-online/article/zeit',
    'http://localhost:9090/zeit-online/article/zplus-zeit?C1-Meter-Status=always_paid',
    'http://localhost:9090/zeit-online/basic-teasers-setup',
    'http://localhost:9090/zeit-online/centerpage/print-ressort',
    'http://localhost:9090/zeit-online/centerpage/teasers-to-campus',
    'http://localhost:9090/zeit-online/centerpage/zplus',
    'http://localhost:9090/zeit-online/journalistic-formats',
    'http://localhost:9090/zeit-online/main-teaser-setup',
    'http://localhost:9090/zeit-online/storystream/dummy',
    'http://localhost:9090/zeit-online/thema',
    'http://localhost:9090/zeit-online/topic-teaser',
    'http://localhost:9090/zeit-online/video-stage'
  ]

    // wait einführen fürs Laden der Bilder.

  casper.start().each(links, function (self, link) {
    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(1920, 1080).then(function () {
        this.wait(2000, function () {
          phantomcss.screenshot('html', filename + '_fullscreen_desktop')
        })
      })
    })

    self.thenOpen(link, function () {
      var filename = urlToFilename(this.getCurrentUrl())
      casper.viewport(360, 600).then(function () {
        this.wait(2000, function () {
          phantomcss.screenshot('html', filename + '_fullscreen_mobile')
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
