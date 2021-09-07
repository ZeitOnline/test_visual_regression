/**
 * example engine script for setting user prefers color scheme
 * would be used as `onBeforeScript` in scenario
 *
 * @param {object}  page  the puppeteer page object
 * @see   https://github.com/garris/BackstopJS#running-custom-scripts
 * @see   https://github.com/puppeteer/puppeteer/blob/v10.2.0/docs/api.md#class-page
 */

module.exports = async page => {
  await page.emulateMediaFeatures([
    { name: 'prefers-color-scheme', value: 'dark' },
  ]);

};
