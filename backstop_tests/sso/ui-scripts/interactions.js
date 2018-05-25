module.exports = function (casper, scenario, vp) {
  // Submit form
  casper.echo('Clicking Submitbtn')
  casper.click('input[type="submit"]')
  casper.wait(1000)
}
