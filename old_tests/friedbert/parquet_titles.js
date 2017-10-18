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
    screenshotRoot: fs.absolute(fs.workingDirectory + '/screenshots/parquet_titles'),
    failedComparisonsRoot: fs.absolute(fs.workingDirectory + '/failures/parquet_titles'),
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
    'http://localhost:9090/zeit-online/parquet'
  ]

  casper.start()

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
        var parquetTitles = casper.evaluate(function () {
          return [].map.call(__utils__.findAll('.parquet-meta__title'), function (node) {
            var modifier = node.getAttribute('class').split('--')[1]
            if (modifier) {
              return '.parquet-meta__title' + '--' + modifier
            } else {
              return '.parquet-meta__title'
            }
          })
        })
        function captureTitle (elem) {
          phantomcss.screenshot(elem, 'mobile_' + elem.replace('.', ''))
        }
        // remove duplicates from array
        var uniqueTitles = parquetTitles.filter(function (elem, pos) {
          return parquetTitles.indexOf(elem) === pos
        })
        // capture screenshots of singled out parquet titles
        uniqueTitles.forEach(captureTitle)
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
