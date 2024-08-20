module.exports = function (casper, _scenario, _vp) {
  // Submit form
  casper.echo('Clicking Submitbtn')
  casper.click('input[type="submit"]')
  casper.wait(1000)
}
