/**
 * example engine script for setting user prefers color scheme
 * would be used as `onBeforeScript` in scenario
 *
 * @param {object}  page  the puppeteer page object
 * @param {object}  scenario  currently running scenario config
 * @see   https://github.com/garris/BackstopJS#running-custom-scripts
 * @see   https://github.com/puppeteer/puppeteer/blob/v10.2.0/docs/api.md#class-page
 */

module.exports = async (page, scenario) => {
  console.log('SCENARIO > ' + scenario.label);

  await page.emulateMediaFeatures([
    { name: 'prefers-color-scheme', value: 'dark' },
  ]);

};
