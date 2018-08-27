// import all zmo files
const article = require( `./article.js` );
const base = require( `./base.js` );
const centerpage = require( `./centerpage.js` );
const leben = require( `./leben.js` );
const mode = require( `./mode-design.js` );
const legacy = require( `./test-cp-legacy.js` );

module.exports = [].concat(
  base,
  article,
  centerpage,
  leben,
  mode,
  legacy
);