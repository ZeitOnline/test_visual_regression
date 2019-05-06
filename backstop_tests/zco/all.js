// import all zco files
const base = require( `./base.js` );
const embedheader = require( `./embedheader.js` );
const paywall = require( `./paywall.js` );
const amp = require( `./amp.js` );

module.exports = [].concat(
  base,
  embedheader,
  paywall,
  amp
);
