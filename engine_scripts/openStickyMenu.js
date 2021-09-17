module.exports = async page => {
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    /*eslint-env browser*/
    window.scrollTo({
      top: 800,
      left: 0,
      behavior: 'smooth'
    });
    window.scrollTo({
      top: 600,
      left: 0,
      behavior: 'smooth'
    });
  });
  await page.waitForSelector('.header--floating');
  await page.click('.header--floating .header__menu-link');
};
